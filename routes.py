"""
Rutas principales de la API REST.
Endpoints para crear reels, consultar estado y descargar.
"""

import os
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.models.reel import ReelRequest, ReelResponse, ReelJob
from app.services import job_manager
from app.config import settings

router = APIRouter(prefix="/api", tags=["reels"])


@router.post("/generate", response_model=ReelResponse, status_code=202)
async def generate_reel(
    request: ReelRequest,
    background_tasks: BackgroundTasks
):
    """
    Inicia la generación de un reel.

    - Crea un trabajo en cola
    - Procesa en background (asíncrono)
    - Retorna el job_id para consultar el estado
    """
    # Crear trabajo y obtener ID
    job_id = job_manager.create_job()

    # Lanzar procesamiento en background
    background_tasks.add_task(
        job_manager.process_reel_job,
        job_id,
        request
    )

    # Estimar tiempo según cantidad de escenas
    estimated = request.duration_seconds * 4  # ~4s de procesamiento por segundo de video

    return ReelResponse(
        job_id=job_id,
        message="Generación iniciada. Consulta el estado con el job_id.",
        estimated_time_seconds=estimated
    )


@router.get("/status/{job_id}", response_model=ReelJob)
async def get_job_status(job_id: str):
    """
    Consulta el estado actual de un trabajo de generación.

    Estados posibles:
    - pending: En cola
    - generating_script: Creando guion con IA
    - generating_audio: Generando voz en off
    - generating_images: Creando imágenes de escenas
    - composing_video: Ensamblando video con FFmpeg
    - completed: Listo para descargar
    - failed: Error durante la generación
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return job


@router.get("/download/{job_id}")
async def download_reel(job_id: str):
    """
    Descarga el video MP4 generado.
    Solo disponible cuando el estado es 'completed'.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")

    if job.status.value != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"El video no está listo. Estado actual: {job.status.value}"
        )

    video_path = os.path.join(settings.output_dir, f"{job_id}.mp4")

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Archivo de video no encontrado")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"reel_{job_id[:8]}.mp4",
        headers={"Content-Disposition": f"attachment; filename=reel_{job_id[:8]}.mp4"}
    )


@router.get("/preview/{job_id}")
async def preview_reel(job_id: str):
    """
    Vista previa del video (stream en el navegador, sin descargar).
    """
    job = job_manager.get_job(job_id)
    if not job or job.status.value != "completed":
        raise HTTPException(status_code=404, detail="Video no disponible")

    video_path = os.path.join(settings.output_dir, f"{job_id}.mp4")

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        headers={"Accept-Ranges": "bytes"}
    )


@router.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """Elimina un trabajo y sus archivos asociados."""
    import shutil
    from app.services import job_manager

    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")

    # Eliminar archivos temporales
    job_temp_dir = os.path.join(settings.temp_dir, job_id)
    if os.path.exists(job_temp_dir):
        shutil.rmtree(job_temp_dir)

    # Eliminar video de salida
    video_path = os.path.join(settings.output_dir, f"{job_id}.mp4")
    if os.path.exists(video_path):
        os.remove(video_path)

    return {"message": "Trabajo eliminado correctamente"}


@router.get("/health")
async def health_check():
    """Verificación de salud del servidor."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "apis": {
            "openai": bool(settings.openai_api_key),
            "elevenlabs": bool(settings.elevenlabs_api_key),
            "stability": bool(settings.stability_api_key),
            "pexels": bool(settings.pexels_api_key),
        }
    }
