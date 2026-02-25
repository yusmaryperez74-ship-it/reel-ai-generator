"""
Configuración centralizada de la aplicación.
Lee variables de entorno con valores por defecto seguros.
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    stability_api_key: str = ""
    pexels_api_key: str = ""

    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Directorios
    temp_dir: str = "/tmp/reel_ai"
    output_dir: str = "/tmp/reel_ai/output"
    max_file_age_hours: int = 24

    # Video
    video_width: int = 1080
    video_height: int = 1920
    video_fps: int = 30
    video_duration_max: int = 60

    # AWS (opcional)
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket_name: str = ""
    aws_region: str = "us-east-1"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


# Instancia global de configuración
settings = Settings()

# Crear directorios necesarios al importar
os.makedirs(settings.temp_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)
os.makedirs(os.path.join(settings.temp_dir, "audio"), exist_ok=True)
os.makedirs(os.path.join(settings.temp_dir, "images"), exist_ok=True)
os.makedirs(os.path.join(settings.temp_dir, "music"), exist_ok=True)
