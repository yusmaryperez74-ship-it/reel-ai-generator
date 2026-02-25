# Reel AI Generator

Genera reels virales para Instagram automáticamente con Inteligencia Artificial.
Escribe el tema y la IA crea el guion, voz en off, imágenes, subtítulos y exporta en MP4 9:16.

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Backend | Python 3.11 + FastAPI |
| Generación de guion | OpenAI GPT-4o |
| Voz en off | ElevenLabs Multilingual v2 (fallback: OpenAI TTS) |
| Imágenes | DALL-E 3 (fallback: Pexels API) |
| Video | FFmpeg (slideshow + Ken Burns + subtítulos SRT) |
| Cola de tareas | Asyncio (desarrollo) / Celery + Redis (producción) |

---

## Estructura del proyecto

```
reel-ai-generator/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py           # Endpoints REST
│   │   ├── models/
│   │   │   └── reel.py             # Modelos Pydantic
│   │   ├── services/
│   │   │   ├── script_generator.py # GPT-4: generación de guion
│   │   │   ├── tts_service.py      # ElevenLabs / OpenAI TTS
│   │   │   ├── image_generator.py  # DALL-E 3 / Pexels
│   │   │   ├── video_composer.py   # FFmpeg pipeline
│   │   │   └── job_manager.py      # Orquestador de tareas
│   │   ├── config.py               # Variables de entorno
│   │   └── main.py                 # Punto de entrada FastAPI
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ReelForm.tsx        # Formulario de configuración
│   │   │   ├── ProgressPanel.tsx   # Panel de progreso en tiempo real
│   │   │   ├── ScriptViewer.tsx    # Visualizador del guion generado
│   │   │   └── VideoResult.tsx     # Reproductor y descarga
│   │   ├── hooks/
│   │   │   └── useReelGenerator.ts # Hook principal de estado
│   │   ├── services/
│   │   │   └── api.ts              # Cliente HTTP para el backend
│   │   ├── styles/
│   │   │   └── globals.css         # Estilos Tailwind globales
│   │   ├── App.tsx                 # Componente raíz
│   │   └── main.tsx                # Entry point React
│   ├── package.json
│   └── vite.config.ts
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docker-compose.yml
└── README.md
```

---

## Instalación y ejecución local

### Prerrequisitos

- Python 3.11+
- Node.js 18+
- FFmpeg instalado en el sistema
- Al menos una API key (OpenAI es la mínima requerida)

### Instalar FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg

# Windows
winget install ffmpeg
```

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/reel-ai-generator.git
cd reel-ai-generator
```

### 2. Configurar el Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
# o: venv\Scripts\activate      # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env   # Completar con tus API keys
```

Editar `.env` con al menos:
```env
OPENAI_API_KEY=sk-...          # Requerido (GPT-4 + DALL-E + TTS fallback)
ELEVENLABS_API_KEY=...         # Opcional (mejor calidad de voz)
PEXELS_API_KEY=...             # Opcional (imágenes stock como fallback)
```

Iniciar el backend:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

El backend estará disponible en: `http://localhost:8000`
Documentación automática: `http://localhost:8000/docs`

### 3. Configurar el Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar en modo desarrollo
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

---

## Flujo completo de generación

```
Usuario escribe tema
        ↓
[POST /api/generate]  →  Crear job_id + task en background
        ↓
GPT-4o genera guion JSON con escenas y prompts visuales
        ↓
ElevenLabs / OpenAI TTS convierte texto → audio MP3 por escena
        ↓
DALL-E 3 genera imagen 1024x1792 por cada escena
        ↓
FFmpeg: imagesequence + Ken Burns effect → video sin audio
        ↓
FFmpeg: video + narración concatenada → video con audio
        ↓
FFmpeg: filtro subtitles SRT estilo TikTok (blanco+negrita)
        ↓
FFmpeg: mezcla música de fondo al 20% de volumen
        ↓
FFmpeg: exportación final H.264, 1080x1920, AAC 192kbps
        ↓
[GET /api/download/{job_id}]  →  Descargar MP4
```

---

## API Reference

### POST /api/generate
Inicia la generación de un reel.

```json
{
  "topic": "5 hábitos que cambiarán tu vida",
  "language": "es",
  "style": "vibrant",
  "voice_gender": "female",
  "music": "upbeat",
  "duration_seconds": 30,
  "add_subtitles": true
}
```

Respuesta `202`:
```json
{
  "job_id": "uuid-del-trabajo",
  "message": "Generación iniciada",
  "estimated_time_seconds": 120
}
```

### GET /api/status/{job_id}
Consulta el estado del trabajo.

```json
{
  "job_id": "...",
  "status": "composing_video",
  "progress": 75,
  "message": "Ensamblando video con FFmpeg...",
  "script": { ... },
  "download_url": null
}
```

Estados posibles: `pending` → `generating_script` → `generating_audio` → `generating_images` → `composing_video` → `completed`

### GET /api/download/{job_id}
Descarga el video MP4 final.

### GET /api/health
Verifica el estado de las APIs configuradas.

---

## Despliegue con Docker

### Desarrollo local completo

```bash
# Desde la raíz del proyecto
cp backend/.env.example backend/.env
# Editar backend/.env con tus API keys

docker-compose up --build
```

Accesos:
- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Despliegue en producción (Railway / Render / VPS)

#### Railway (recomendado para empezar)
```bash
# Instalar Railway CLI
npm install -g @railway/cli
railway login

# Crear nuevo proyecto
railway init
railway up

# Configurar variables de entorno en el dashboard de Railway
```

#### Render.com
1. Crear dos servicios: Web Service (backend) + Static Site (frontend)
2. Backend: `pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Frontend: `npm install && npm run build` → Build directory: `dist`
4. Configurar variables de entorno en el panel de Render

#### VPS (Ubuntu) con Nginx
```bash
# Instalar dependencias
sudo apt install python3.11 nodejs npm ffmpeg nginx

# Backend con Gunicorn + systemd
pip install gunicorn
gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend compilado
npm run build
sudo cp -r dist/* /var/www/html/

# Nginx como reverse proxy (apuntar /api a :8000)
```

---

## APIs necesarias y costos estimados

| API | Uso | Costo estimado por reel |
|-----|-----|------------------------|
| OpenAI GPT-4o | Guion | ~$0.05 |
| OpenAI DALL-E 3 | 4 imágenes HD | ~$0.16 |
| ElevenLabs | ~200 palabras | ~$0.03 |
| Total aproximado | | **~$0.24 por reel** |

> Con Pexels (gratis) en lugar de DALL-E, el costo baja a ~$0.08/reel.

---

## Obtener las API Keys

1. **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. **ElevenLabs**: [elevenlabs.io](https://elevenlabs.io) → Profile → API Key
3. **Pexels**: [pexels.com/api](https://www.pexels.com/api/) (gratuito)

---

## Solución de problemas comunes

**FFmpeg no encontrado:**
```bash
which ffmpeg        # Verificar instalación
# Agregar al PATH si es necesario
export PATH=$PATH:/usr/local/bin
```

**Error "OpenAI API key not valid":**
- Verificar que el .env tiene `OPENAI_API_KEY=sk-...`
- Reiniciar el servidor tras modificar el .env

**Video sin audio:**
- Verificar que los archivos MP3 se generaron en `/tmp/reel_ai/audio/`
- Revisar logs del backend para errores de TTS

**Imágenes negras/placeholder:**
- DALL-E requiere cuenta OpenAI con créditos
- Configurar `PEXELS_API_KEY` como fallback gratuito

---

## Licencia

MIT License - Libre para uso personal y comercial.
