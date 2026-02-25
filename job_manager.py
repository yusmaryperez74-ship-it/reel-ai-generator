"""
Gestor de trabajos en memoria (para desarrollo sin Redis).
En producción, reemplazar con Celery + Redis.
"""

import uuid
import asyncio
from datetime import datetime
from typing import Dict, Optional
from app.models.reel import ReelJob, JobStatus, ReelRequest


# Almacén de trabajos en memoria
_jobs: Dict[str, ReelJob] = {}


def create_job() -> str:
    """Crea un nuevo trabajo y retorna su ID."""
    job_id = str(uuid.uuid4())
    _jobs[job_id] = ReelJob(
        job_id=job_id,
        status=JobStatus.PENDING,
        progress=0,
        message="Trabajo en cola...",
        created_at=datetime.utcnow().isoformat()
    )
    return job_id


def get_job(job_id: str) -> Optional[ReelJob]:
    """Obtiene el estado actual de un trabajo."""
    return _jobs.get(job_id)


def update_job(
    job_id: str,
    status: JobStatus,
    progress: int,
    message: str,
    **kwargs
) -> None:
    """Actualiza el estado de un trabajo."""
    if job_id in _jobs:
        job = _jobs[job_id]
        job.status = status
        job.progress = progress
        job.message = message
        for key, value in kwargs.items():
            setattr(job, key, value)


def fail_job(job_id: str, error: str) -> None:
    """Marca un trabajo como fallido."""
    if job_id in _jobs:
        _jobs[job_id].status = JobStatus.FAILED
        _jobs[job_id].error = error
        _jobs[job_id].message = "Error en la generación"
        _jobs[job_id].progress = 0


async def process_reel_job(job_id: str, request: ReelRequest) -> None:
    """
    Orquesta el proceso completo de generación del reel.
    Se ejecuta en background como tarea asíncrona.
    """
    from app.services.script_generator import ScriptGeneratorService
    from app.services.tts_service import TTSService
    from app.services.image_generator import ImageGeneratorService
    from app.services.video_composer import VideoComposerService
    from app.config import settings
    import os

    try:
        # PASO 1: Generar guion
        update_job(job_id, JobStatus.GENERATING_SCRIPT, 10,
                   "Generando guion viral con IA...")

        script_svc = ScriptGeneratorService()
        script = await script_svc.generate(
            topic=request.topic,
            language=request.language,
            duration_seconds=request.duration_seconds,
            style=request.style.value
        )

        update_job(job_id, JobStatus.GENERATING_SCRIPT, 25,
                   "Guion generado. Generando voz en off...",
                   script=script)

        # PASO 2: Generar audio (TTS)
        update_job(job_id, JobStatus.GENERATING_AUDIO, 30,
                   "Convirtiendo guion a voz realista...")

        tts_svc = TTSService()
        audio_files = await tts_svc.generate_audio(
            script=script,
            job_id=job_id,
            voice_gender=request.voice_gender
        )

        update_job(job_id, JobStatus.GENERATING_AUDIO, 50,
                   "Voz generada. Creando escenas visuales con IA...")

        # PASO 3: Generar imágenes
        update_job(job_id, JobStatus.GENERATING_IMAGES, 55,
                   "Generando imágenes para cada escena...")

        img_svc = ImageGeneratorService()
        image_files = await img_svc.generate_scene_images(
            scenes=script.scenes,
            job_id=job_id,
            style=request.style
        )

        update_job(job_id, JobStatus.GENERATING_IMAGES, 70,
                   "Imágenes listas. Componiendo el video final...")

        # PASO 4: Generar subtítulos SRT
        srt_content = ""
        if request.add_subtitles:
            srt_content = await script_svc.generate_subtitles_srt(script)

        # PASO 5: Componer video final
        update_job(job_id, JobStatus.COMPOSING_VIDEO, 75,
                   "Ensamblando video con FFmpeg...")

        composer = VideoComposerService()
        video_path = await composer.compose(
            script=script,
            image_files=image_files,
            audio_files=audio_files,
            job_id=job_id,
            add_subtitles=request.add_subtitles,
            music_genre=request.music,
            srt_content=srt_content
        )

        update_job(
            job_id,
            JobStatus.COMPLETED,
            100,
            "Reel generado exitosamente",
            download_url=f"/api/download/{job_id}"
        )

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[JobManager] Error en job {job_id}: {error_detail}")
        fail_job(job_id, str(e))
