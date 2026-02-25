"""
Punto de entrada principal de la aplicación FastAPI.
Configura middleware, rutas y eventos de ciclo de vida.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre de la aplicación."""
    # Inicio: verificar dependencias
    print("=" * 50)
    print("🎬 REEL AI GENERATOR - Iniciando servidor...")
    print(f"   Puerto: {settings.port}")
    print(f"   OpenAI: {'✅' if settings.openai_api_key else '❌ No configurado'}")
    print(f"   ElevenLabs: {'✅' if settings.elevenlabs_api_key else '⚠️  Usará OpenAI TTS'}")
    print(f"   Pexels: {'✅' if settings.pexels_api_key else '⚠️  Sin imágenes stock'}")
    print(f"   Directorio temporal: {settings.temp_dir}")
    print("=" * 50)

    yield

    # Cierre: limpieza opcional
    print("Servidor detenido.")


app = FastAPI(
    title="Reel AI Generator API",
    description="API para generación automática de Instagram Reels con IA",
    version="1.0.0",
    lifespan=lifespan
)

# ---- Configuración de CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Rutas de la API ----
app.include_router(router)

# ---- Servir archivos estáticos generados ----
os.makedirs(settings.output_dir, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")

# ---- Ruta raíz ----
@app.get("/")
async def root():
    return {
        "name": "Reel AI Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
