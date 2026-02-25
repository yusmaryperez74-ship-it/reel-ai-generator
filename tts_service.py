"""
Servicio de Text-to-Speech.
Usa ElevenLabs como primaria y OpenAI TTS como fallback.
"""

import os
import aiofiles
from pathlib import Path
from openai import AsyncOpenAI
from app.config import settings
from app.models.reel import ReelScript, VoiceGender


class TTSService:
    """Convierte texto a voz usando IA."""

    # Mapeo de voces ElevenLabs por género
    ELEVENLABS_VOICES = {
        VoiceGender.FEMALE: "21m00Tcm4TlvDq8ikWAM",  # Rachel
        VoiceGender.MALE: "AZnzlk1XvdvUeBnXmlld",    # Domi
    }

    # Mapeo de voces OpenAI TTS por género
    OPENAI_VOICES = {
        VoiceGender.FEMALE: "nova",
        VoiceGender.MALE: "onyx",
    }

    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.openai_api_key)
        self.audio_dir = os.path.join(settings.temp_dir, "audio")

    async def generate_audio(
        self,
        script: ReelScript,
        job_id: str,
        voice_gender: VoiceGender = VoiceGender.FEMALE
    ) -> list[str]:
        """
        Genera archivos de audio para cada escena del guion.

        Args:
            script: El guion completo
            job_id: ID único del trabajo
            voice_gender: Género de la voz

        Returns:
            Lista de rutas a los archivos de audio generados
        """
        audio_files = []

        # Crear directorio para este job
        job_audio_dir = os.path.join(self.audio_dir, job_id)
        os.makedirs(job_audio_dir, exist_ok=True)

        # Incluir el hook en la primera escena si no está
        all_texts = []
        for scene in script.scenes:
            all_texts.append((scene.order, scene.text, scene.duration))

        for order, text, duration in all_texts:
            output_path = os.path.join(job_audio_dir, f"scene_{order:02d}.mp3")

            # Intentar ElevenLabs primero, fallback a OpenAI
            if settings.elevenlabs_api_key:
                success = await self._generate_elevenlabs(
                    text, output_path, voice_gender
                )
            else:
                success = False

            if not success:
                await self._generate_openai_tts(text, output_path, voice_gender)

            audio_files.append(output_path)

        return audio_files

    async def _generate_elevenlabs(
        self,
        text: str,
        output_path: str,
        voice_gender: VoiceGender
    ) -> bool:
        """
        Genera audio con ElevenLabs API.
        Retorna True si fue exitoso.
        """
        try:
            import httpx

            voice_id = self.ELEVENLABS_VOICES.get(
                voice_gender,
                settings.elevenlabs_voice_id
            )

            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": settings.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    async with aiofiles.open(output_path, "wb") as f:
                        await f.write(response.content)
                    return True

            return False

        except Exception as e:
            print(f"[TTS] ElevenLabs falló: {e}. Usando OpenAI TTS.")
            return False

    async def _generate_openai_tts(
        self,
        text: str,
        output_path: str,
        voice_gender: VoiceGender
    ) -> None:
        """Genera audio con OpenAI TTS como fallback."""
        voice = self.OPENAI_VOICES.get(voice_gender, "nova")

        response = await self.openai.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=text,
            speed=1.05  # Ligeramente más rápido para reels
        )

        # Guardar archivo de audio
        async with aiofiles.open(output_path, "wb") as f:
            await f.write(response.content)

    async def get_audio_duration(self, audio_path: str) -> float:
        """Obtiene la duración de un archivo de audio usando ffprobe."""
        import asyncio
        import json

        proc = await asyncio.create_subprocess_exec(
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            audio_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()

        try:
            info = json.loads(stdout)
            return float(info["streams"][0]["duration"])
        except Exception:
            return 5.0  # Duración por defecto si falla
