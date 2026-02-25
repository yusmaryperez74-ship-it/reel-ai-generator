"""
Servicio de generación de imágenes para las escenas del reel.
Usa DALL-E 3 como principal y Pexels como fallback de imágenes stock.
"""

import os
import httpx
import aiofiles
from openai import AsyncOpenAI
from app.config import settings
from app.models.reel import ScriptScene, VideoStyle


class ImageGeneratorService:
    """Genera imágenes para cada escena del reel."""

    # Modificadores de estilo visual para los prompts
    STYLE_MODIFIERS = {
        VideoStyle.CINEMATIC: "cinematic photography, dramatic lighting, shallow depth of field, film grain, 8K ultra realistic",
        VideoStyle.VIBRANT: "vibrant colors, bright lighting, modern aesthetic, Instagram-worthy, professional photography",
        VideoStyle.MINIMAL: "minimalist composition, clean background, subtle colors, modern design, editorial photography",
        VideoStyle.DARK: "dark moody aesthetic, contrast lighting, dramatic shadows, cinematic dark tones, premium feel",
    }

    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.openai_api_key)
        self.images_dir = os.path.join(settings.temp_dir, "images")

    async def generate_scene_images(
        self,
        scenes: list[ScriptScene],
        job_id: str,
        style: VideoStyle = VideoStyle.VIBRANT
    ) -> list[str]:
        """
        Genera imágenes para todas las escenas del reel.

        Args:
            scenes: Lista de escenas con sus prompts visuales
            job_id: ID único del trabajo
            style: Estilo visual a aplicar

        Returns:
            Lista de rutas a las imágenes generadas
        """
        job_images_dir = os.path.join(self.images_dir, job_id)
        os.makedirs(job_images_dir, exist_ok=True)

        image_files = []
        style_mod = self.STYLE_MODIFIERS.get(style, self.STYLE_MODIFIERS[VideoStyle.VIBRANT])

        for scene in scenes:
            output_path = os.path.join(job_images_dir, f"scene_{scene.order:02d}.png")

            # Construir prompt enriquecido con el estilo
            enhanced_prompt = (
                f"{scene.visual_prompt}, {style_mod}, "
                f"vertical composition 9:16 portrait format, high quality"
            )

            # Intentar DALL-E 3, fallback a Pexels
            success = await self._generate_dalle(enhanced_prompt, output_path)

            if not success:
                # Buscar imagen relacionada en Pexels
                search_query = self._extract_keywords(scene.visual_prompt)
                success = await self._fetch_pexels_image(search_query, output_path)

            if not success:
                # Último fallback: generar imagen sólida de color
                await self._generate_placeholder(output_path, scene.order)

            image_files.append(output_path)

        return image_files

    async def _generate_dalle(self, prompt: str, output_path: str) -> bool:
        """Genera imagen con DALL-E 3."""
        if not settings.openai_api_key:
            return False

        try:
            response = await self.openai.images.generate(
                model="dall-e-3",
                prompt=prompt[:4000],  # DALL-E tiene límite de caracteres
                size="1024x1792",      # Formato vertical 9:16
                quality="hd",
                n=1,
                style="vivid"
            )

            image_url = response.data[0].url

            # Descargar la imagen generada
            async with httpx.AsyncClient(timeout=60.0) as client:
                img_response = await client.get(image_url)
                if img_response.status_code == 200:
                    async with aiofiles.open(output_path, "wb") as f:
                        await f.write(img_response.content)
                    return True

            return False

        except Exception as e:
            print(f"[ImageGen] DALL-E falló para escena: {e}")
            return False

    async def _fetch_pexels_image(self, query: str, output_path: str) -> bool:
        """Obtiene imagen de stock de Pexels como fallback."""
        if not settings.pexels_api_key:
            return False

        try:
            headers = {"Authorization": settings.pexels_api_key}
            params = {
                "query": query,
                "per_page": 1,
                "orientation": "portrait"  # Vertical para reels
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://api.pexels.com/v1/search",
                    headers=headers,
                    params=params
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("photos"):
                        img_url = data["photos"][0]["src"]["large2x"]
                        img_response = await client.get(img_url)
                        if img_response.status_code == 200:
                            async with aiofiles.open(output_path, "wb") as f:
                                await f.write(img_response.content)
                            return True

            return False

        except Exception as e:
            print(f"[ImageGen] Pexels falló: {e}")
            return False

    async def _generate_placeholder(self, output_path: str, scene_number: int) -> None:
        """Genera imagen placeholder con gradiente como último recurso."""
        from PIL import Image, ImageDraw, ImageFont
        import random

        # Paletas de colores para gradientes
        color_palettes = [
            [(48, 25, 52), (89, 57, 161)],    # Púrpura
            [(26, 35, 126), (21, 101, 192)],   # Azul
            [(27, 94, 32), (56, 142, 60)],     # Verde
            [(183, 28, 28), (229, 57, 53)],    # Rojo
            [(230, 81, 0), (255, 143, 0)],     # Naranja
        ]

        colors = color_palettes[scene_number % len(color_palettes)]

        img = Image.new("RGB", (settings.video_width, settings.video_height))
        draw = ImageDraw.Draw(img)

        # Dibujar gradiente vertical
        for y in range(settings.video_height):
            ratio = y / settings.video_height
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio)
            draw.line([(0, y), (settings.video_width, y)], fill=(r, g, b))

        img.save(output_path, "PNG")

    def _extract_keywords(self, visual_prompt: str) -> str:
        """Extrae palabras clave del prompt visual para buscar en Pexels."""
        # Tomar las primeras 3-4 palabras más significativas
        stop_words = {"a", "an", "the", "of", "in", "on", "at", "for", "with", "and"}
        words = [w for w in visual_prompt.split()[:10] if w.lower() not in stop_words]
        return " ".join(words[:4])
