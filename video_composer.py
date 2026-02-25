"""
Servicio de composición de video con FFmpeg.
Ensambla imágenes, audio, subtítulos y música en un reel vertical 9:16.
"""

import os
import asyncio
import aiofiles
from pathlib import Path
from app.config import settings
from app.models.reel import ReelScript, MusicGenre


class VideoComposerService:
    """Compone el video final del reel usando FFmpeg."""

    # Rutas de música de fondo incluidas (archivos locales)
    MUSIC_FILES = {
        MusicGenre.UPBEAT: "music/upbeat.mp3",
        MusicGenre.AMBIENT: "music/ambient.mp3",
        MusicGenre.DRAMATIC: "music/dramatic.mp3",
        MusicGenre.MOTIVATIONAL: "music/motivational.mp3",
    }

    def __init__(self):
        self.output_dir = settings.output_dir
        self.temp_dir = settings.temp_dir
        self.width = settings.video_width
        self.height = settings.video_height
        self.fps = settings.video_fps

    async def compose(
        self,
        script: ReelScript,
        image_files: list[str],
        audio_files: list[str],
        job_id: str,
        add_subtitles: bool = True,
        music_genre: MusicGenre = MusicGenre.UPBEAT,
        srt_content: str = ""
    ) -> str:
        """
        Ensambla el video completo del reel.

        Args:
            script: El guion con metadatos
            image_files: Rutas a las imágenes de cada escena
            audio_files: Rutas a los audios de cada escena
            job_id: ID único del trabajo
            add_subtitles: Si se añaden subtítulos estilo TikTok
            music_genre: Tipo de música de fondo
            srt_content: Contenido del archivo SRT

        Returns:
            Ruta al video final MP4
        """
        job_dir = os.path.join(self.temp_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)

        # Paso 1: Combinar audio de todas las escenas en uno solo
        combined_audio = os.path.join(job_dir, "narration.mp3")
        await self._concat_audio(audio_files, combined_audio)

        # Paso 2: Obtener duración total del audio
        total_duration = await self._get_duration(combined_audio)

        # Paso 3: Crear video con imágenes (slideshow animado)
        raw_video = os.path.join(job_dir, "raw_video.mp4")
        await self._create_image_slideshow(
            image_files, script.scenes, raw_video, total_duration
        )

        # Paso 4: Agregar audio de narración al video
        video_with_audio = os.path.join(job_dir, "with_audio.mp4")
        await self._add_audio_to_video(raw_video, combined_audio, video_with_audio)

        # Paso 5: Agregar subtítulos si se requieren
        if add_subtitles and srt_content:
            srt_path = os.path.join(job_dir, "subtitles.srt")
            async with aiofiles.open(srt_path, "w", encoding="utf-8") as f:
                await f.write(srt_content)

            video_with_subs = os.path.join(job_dir, "with_subs.mp4")
            await self._add_subtitles(video_with_audio, srt_path, video_with_subs)
            current_video = video_with_subs
        else:
            current_video = video_with_audio

        # Paso 6: Agregar música de fondo (si se seleccionó)
        if music_genre != MusicGenre.NONE:
            video_with_music = os.path.join(job_dir, "with_music.mp4")
            await self._add_background_music(
                current_video, music_genre, video_with_music
            )
            current_video = video_with_music

        # Paso 7: Exportación final optimizada para Instagram
        final_output = os.path.join(self.output_dir, f"{job_id}.mp4")
        await self._export_final(current_video, final_output)

        return final_output

    async def _concat_audio(self, audio_files: list[str], output: str) -> None:
        """Concatena múltiples archivos de audio en uno."""
        # Crear archivo de lista para FFmpeg
        list_file = output.replace(".mp3", "_list.txt")
        async with aiofiles.open(list_file, "w") as f:
            for af in audio_files:
                await f.write(f"file '{af}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output
        ]
        await self._run_ffmpeg(cmd)

    async def _get_duration(self, media_file: str) -> float:
        """Obtiene la duración de un archivo de media."""
        proc = await asyncio.create_subprocess_exec(
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            media_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        try:
            return float(stdout.decode().strip())
        except ValueError:
            return 30.0

    async def _create_image_slideshow(
        self,
        image_files: list[str],
        scenes,
        output: str,
        total_duration: float
    ) -> None:
        """
        Crea un slideshow animado con zoom/pan (efecto Ken Burns) en cada imagen.
        """
        if not image_files:
            raise ValueError("No hay imágenes para crear el video")

        # Calcular duración de cada escena
        durations = [s.duration for s in scenes]
        if len(durations) != len(image_files):
            per_image = total_duration / len(image_files)
            durations = [per_image] * len(image_files)

        # Construir filtro complejo de FFmpeg para el slideshow con zoom
        inputs = []
        filter_parts = []
        concat_inputs = []

        for i, (img_path, duration) in enumerate(zip(image_files, durations)):
            inputs.extend(["-loop", "1", "-t", str(duration), "-i", img_path])

            # Efecto Ken Burns: zoom in sutil
            zoom_filter = (
                f"[{i}:v]"
                f"scale={self.width * 2}:{self.height * 2},"
                f"zoompan=z='min(zoom+0.0015,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={int(duration * self.fps)}:s={self.width}x{self.height}:fps={self.fps},"
                f"setsar=1[v{i}]"
            )
            filter_parts.append(zoom_filter)
            concat_inputs.append(f"[v{i}]")

        # Concatenar todas las escenas
        n = len(image_files)
        concat_filter = f"{''.join(concat_inputs)}concat=n={n}:v=1:a=0[vout]"
        filter_parts.append(concat_filter)

        full_filter = ";".join(filter_parts)

        cmd = (
            ["ffmpeg", "-y"] +
            inputs +
            [
                "-filter_complex", full_filter,
                "-map", "[vout]",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                output
            ]
        )
        await self._run_ffmpeg(cmd)

    async def _add_audio_to_video(
        self,
        video: str,
        audio: str,
        output: str
    ) -> None:
        """Combina video e audio de narración."""
        cmd = [
            "ffmpeg", "-y",
            "-i", video,
            "-i", audio,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output
        ]
        await self._run_ffmpeg(cmd)

    async def _add_subtitles(
        self,
        video: str,
        srt_path: str,
        output: str
    ) -> None:
        """
        Añade subtítulos estilo TikTok: texto grande, negrita, con sombra.
        Usa el filtro subtitles de FFmpeg.
        """
        # Estilo de subtítulos: blanco, negrita, sombra negra, posición inferior-centro
        subtitle_style = (
            "FontName=Arial,"
            "FontSize=22,"
            "Bold=1,"
            "PrimaryColour=&H00FFFFFF,"    # Blanco
            "OutlineColour=&H00000000,"    # Contorno negro
            "BackColour=&H80000000,"       # Fondo semitransparente
            "Outline=3,"
            "Shadow=2,"
            "Alignment=2,"                 # Centro inferior
            "MarginV=80"                   # Margen desde abajo
        )

        # Escapar la ruta del archivo SRT para FFmpeg
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")

        cmd = [
            "ffmpeg", "-y",
            "-i", video,
            "-vf", f"subtitles={srt_escaped}:force_style='{subtitle_style}'",
            "-c:a", "copy",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            output
        ]
        await self._run_ffmpeg(cmd)

    async def _add_background_music(
        self,
        video: str,
        music_genre: MusicGenre,
        output: str
    ) -> None:
        """Mezcla música de fondo con el audio de narración."""
        # Buscar archivo de música (incluido en el proyecto)
        music_rel = self.MUSIC_FILES.get(music_genre)
        music_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", music_rel or ""
        )

        if not os.path.exists(music_path):
            # Si no existe el archivo de música, copiar el video sin cambios
            import shutil
            shutil.copy(video, output)
            return

        # Mezclar: narración al 100%, música al 20% de volumen
        cmd = [
            "ffmpeg", "-y",
            "-i", video,
            "-stream_loop", "-1",   # Loop infinito de música
            "-i", music_path,
            "-filter_complex",
            "[1:a]volume=0.2[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=3[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output
        ]
        await self._run_ffmpeg(cmd)

    async def _export_final(self, video: str, output: str) -> None:
        """
        Exporta el video final optimizado para Instagram.
        Formato: H.264, 1080x1920, AAC 192kbps.
        """
        cmd = [
            "ffmpeg", "-y",
            "-i", video,
            "-c:v", "libx264",
            "-preset", "slow",       # Mayor compresión para menor tamaño
            "-crf", "20",            # Alta calidad visual
            "-profile:v", "high",
            "-level", "4.0",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-movflags", "+faststart",  # Optimizado para streaming web
            "-vf", f"scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2",
            "-r", str(self.fps),
            "-pix_fmt", "yuv420p",
            output
        ]
        await self._run_ffmpeg(cmd)

    async def _run_ffmpeg(self, cmd: list[str]) -> None:
        """Ejecuta un comando FFmpeg de forma asíncrona."""
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode()
            raise RuntimeError(f"FFmpeg error (código {proc.returncode}): {error_msg[-500:]}")
