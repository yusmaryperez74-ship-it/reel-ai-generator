# ⚡ Inicio Rápido - 3 minutos

## Ejecución local (desarrollo)

### 1️⃣ Requisitos previos

```bash
# Verificar instalaciones
python --version   # Necesitas 3.11+
node --version     # Necesitas 18+
ffmpeg -version    # Debe estar instalado

# Si falta FFmpeg:
# macOS:    brew install ffmpeg
# Ubuntu:   sudo apt install ffmpeg
# Windows:  winget install ffmpeg
```

### 2️⃣ Configurar API Key (solo OpenAI es obligatorio)

```bash
cd backend
cp .env.example .env
nano .env
```

Edita y pega tu API key:
```env
OPENAI_API_KEY=sk-proj-TU_KEY_AQUI
```

**Obtener tu API key:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 3️⃣ Iniciar Backend (terminal 1)

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate    # Mac/Linux
# venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

✅ Backend listo en: `http://localhost:8000`

### 4️⃣ Iniciar Frontend (terminal 2, nueva pestaña)

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar desarrollo
npm run dev
```

✅ App lista en: `http://localhost:5173`

### 5️⃣ Probar

1. Abre `http://localhost:5173` en tu navegador
2. Escribe un tema (ej: "3 trucos para ahorrar dinero")
3. Click en "Crear Reel con IA"
4. Espera ~2 minutos
5. Descarga tu video MP4 9:16 listo para Instagram

---

## Despliegue en producción (Render)

Ver guía completa en: **[DEPLOY_RENDER.md](./DEPLOY_RENDER.md)**

**Resumen ultra rápido:**
```bash
# 1. Subir a GitHub
git init && git add . && git commit -m "Initial"
git remote add origin https://github.com/TU-USER/reel-ai-generator.git
git push -u origin main

# 2. Ir a render.com → New Blueprint → Conectar repo
# 3. Configurar OPENAI_API_KEY en las variables de entorno
# 4. Esperar 10 minutos → Tu app estará online
```

---

## Solución rápida de problemas

**❌ "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**❌ "FFmpeg not found"**
```bash
# Instalar FFmpeg (ver paso 1)
which ffmpeg  # Debe mostrar la ruta
```

**❌ "OpenAI API key not valid"**
- Verifica que copiaste la key completa (empieza con `sk-`)
- Reinicia el servidor backend tras editar .env
- Verifica créditos en: [platform.openai.com/usage](https://platform.openai.com/usage)

**❌ Frontend no conecta con backend**
- Backend debe estar corriendo en puerto 8000
- Verifica en: `http://localhost:8000/api/health`

**❌ Video sin audio**
- Revisa logs del backend (terminal 1)
- Verifica que hay archivos MP3 en `/tmp/reel_ai/audio/`

---

## Costos aproximados

| Servicio | Uso | Costo |
|----------|-----|-------|
| OpenAI GPT-4o | Guion | $0.05/reel |
| OpenAI DALL-E 3 | 4 imágenes | $0.16/reel |
| OpenAI TTS | Audio | $0.03/reel |
| **Total por reel** | | **~$0.24** |

**Ejemplo:** $10 de crédito OpenAI = ~40 reels

---

## Próximos pasos

1. **Lee el README.md** para entender la arquitectura completa
2. **Explora el código:**
   - Backend: `backend/app/services/` (lógica de IA)
   - Frontend: `frontend/src/components/` (UI React)
3. **Personaliza:**
   - Añade nuevos estilos visuales en `backend/app/models/reel.py`
   - Cambia colores del frontend en `frontend/tailwind.config.js`
4. **Despliega a producción** con [DEPLOY_RENDER.md](./DEPLOY_RENDER.md)

---

¿Problemas? Revisa los logs del terminal del backend. Casi todos los errores muestran el problema exacto.
