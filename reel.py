"""
Modelos Pydantic para validación de datos del reel.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class VideoStyle(str, Enum):
    """Estilo visual del reel."""
    CINEMATIC = "cinematic"
    VIBRANT = "vibrant"
    MINIMAL = "minimal"
    DARK = "dark"


class VoiceGender(str, Enum):
    """Género de la voz en off."""
    MALE = "male"
    FEMALE = "female"


class MusicGenre(str, Enum):
    """Género musical de fondo."""
    NONE = "none"
    UPBEAT = "upbeat"
    AMBIENT = "ambient"
    DRAMATIC = "dramatic"
    MOTIVATIONAL = "motivational"


class ReelRequest(BaseModel):
    """Solicitud para crear un nuevo reel."""
    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Tema del reel a generar",
        examples=["5 tips para ahorrar dinero en 2024"]
    )
    language: str = Field(
        default="es",
        description="Idioma del contenido (es=español, en=inglés)"
    )
    style: VideoStyle = Field(
        default=VideoStyle.VIBRANT,
        description="Estilo visual del reel"
    )
    voice_gender: VoiceGender = Field(
        default=VoiceGender.FEMALE,
        description="Género de la voz en off"
    )
    music: MusicGenre = Field(
        default=MusicGenre.UPBEAT,
        description="Tipo de música de fondo"
    )
    duration_seconds: int = Field(
        default=30,
        ge=15,
        le=60,
        description="Duración aproximada del reel en segundos"
    )
    add_subtitles: bool = Field(
        default=True,
        description="Añadir subtítulos estilo TikTok"
    )


class ScriptScene(BaseModel):
    """Una escena individual del guion."""
    order: int
    text: str                    # Texto que se narrará
    visual_prompt: str           # Prompt para generar la imagen
    duration: float              # Duración en segundos
    transition: str = "fade"     # Tipo de transición


class ReelScript(BaseModel):
    """Guion completo generado por IA."""
    title: str
    hook: str                    # Frase inicial de enganche
    scenes: List[ScriptScene]
    call_to_action: str
    hashtags: List[str]
    total_duration: float


class JobStatus(str, Enum):
    """Estado del trabajo de generación."""
    PENDING = "pending"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_AUDIO = "generating_audio"
    GENERATING_IMAGES = "generating_images"
    COMPOSING_VIDEO = "composing_video"
    COMPLETED = "completed"
    FAILED = "failed"


class ReelJob(BaseModel):
    """Trabajo de generación de reel."""
    job_id: str
    status: JobStatus
    progress: int = Field(default=0, ge=0, le=100)
    message: str = ""
    download_url: Optional[str] = None
    script: Optional[ReelScript] = None
    error: Optional[str] = None
    created_at: Optional[str] = None


class ReelResponse(BaseModel):
    """Respuesta inicial al crear un reel."""
    job_id: str
    message: str
    estimated_time_seconds: int
