"""
Servicio de generación de guiones con OpenAI GPT-4.
Produce guiones virales optimizados para Instagram Reels / TikTok.
"""

import json
import re
from typing import Optional
from openai import AsyncOpenAI
from app.config import settings
from app.models.reel import ReelScript, ScriptScene


class ScriptGeneratorService:
    """Genera guiones virales usando GPT-4."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(
        self,
        topic: str,
        language: str = "es",
        duration_seconds: int = 30,
        style: str = "vibrant"
    ) -> ReelScript:
        """
        Genera un guion completo para un reel.

        Args:
            topic: Tema del reel
            language: Idioma (es/en)
            duration_seconds: Duración objetivo
            style: Estilo visual

        Returns:
            ReelScript con todas las escenas generadas
        """
        lang_name = "español" if language == "es" else "English"
        scenes_count = max(3, duration_seconds // 8)  # ~8 segundos por escena

        prompt = f"""Eres un experto en content marketing viral para Instagram Reels y TikTok.

Crea un guion completo para un reel sobre: "{topic}"

REQUISITOS:
- Idioma: {lang_name}
- Duración total: ~{duration_seconds} segundos
- Número de escenas: {scenes_count}
- Estilo: {style}
- El hook debe capturar la atención en los primeros 3 segundos
- Lenguaje cercano, directo y con energía
- Optimizado para retención y shares

Responde ÚNICAMENTE con JSON válido siguiendo esta estructura exacta:
{{
  "title": "Título corto del reel",
  "hook": "Frase inicial de enganche muy impactante (máx 10 palabras)",
  "scenes": [
    {{
      "order": 1,
      "text": "Texto que se narrará en voz alta en esta escena",
      "visual_prompt": "Descripción detallada en inglés de la imagen para esta escena, estilo fotográfico/cinematográfico",
      "duration": 8.0,
      "transition": "fade"
    }}
  ],
  "call_to_action": "Llamada a la acción final (sigue para más contenido así)",
  "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5"],
  "total_duration": {duration_seconds}.0
}}

REGLAS PARA visual_prompt: siempre en inglés, estilo cinematográfico, incluye iluminación y composición.
REGLAS para text: en {lang_name}, natural y hablado, sin signos difíciles de pronunciar."""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en creación de contenido viral. Siempre respondes con JSON válido y nada más."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)

        # Construir modelo de datos validado
        scenes = [
            ScriptScene(
                order=s["order"],
                text=s["text"],
                visual_prompt=s["visual_prompt"],
                duration=float(s.get("duration", duration_seconds / scenes_count)),
                transition=s.get("transition", "fade")
            )
            for s in data["scenes"]
        ]

        return ReelScript(
            title=data["title"],
            hook=data["hook"],
            scenes=scenes,
            call_to_action=data["call_to_action"],
            hashtags=data.get("hashtags", []),
            total_duration=float(data.get("total_duration", duration_seconds))
        )

    async def generate_subtitles_srt(self, script: ReelScript) -> str:
        """
        Genera el contenido SRT de subtítulos sincronizados.

        Args:
            script: El guion completo del reel

        Returns:
            Contenido del archivo SRT como string
        """
        srt_lines = []
        index = 1
        current_time = 0.0

        for scene in script.scenes:
            # Dividir el texto en fragmentos de ~5 palabras para efecto TikTok
            words = scene.text.split()
            chunk_size = 5
            chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]

            if not chunks:
                continue

            time_per_chunk = scene.duration / len(chunks)

            for chunk in chunks:
                start = current_time
                end = current_time + time_per_chunk

                start_srt = self._seconds_to_srt_time(start)
                end_srt = self._seconds_to_srt_time(end)

                srt_lines.append(str(index))
                srt_lines.append(f"{start_srt} --> {end_srt}")
                srt_lines.append(" ".join(chunk).upper())  # Mayúsculas estilo TikTok
                srt_lines.append("")

                index += 1
                current_time = end

        return "\n".join(srt_lines)

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convierte segundos a formato SRT HH:MM:SS,mmm."""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
