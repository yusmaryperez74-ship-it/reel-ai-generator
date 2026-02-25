# 🚀 Guía de Despliegue en Render

Render es la plataforma más sencilla para desplegar esta aplicación. Ofrece plan gratuito con 750 horas/mes.

---

## Opción 1: Despliegue automático con Blueprint (Recomendado)

### Paso 1: Subir a GitHub

```bash
cd reel-ai-generator

# Inicializar git
git init
git add .
git commit -m "Initial commit: Reel AI Generator"

# Crear repositorio en GitHub y conectar
git remote add origin https://github.com/TU-USUARIO/reel-ai-generator.git
git branch -M main
git push -u origin main
```

### Paso 2: Desplegar en Render

1. Ve a [render.com](https://render.com) y registrate/inicia sesión
2. Click en **"New +"** → **"Blueprint"**
3. Conecta tu repositorio de GitHub
4. Render detectará automáticamente el `render.yaml`
5. Configura las variables de entorno (ver abajo)
6. Click en **"Apply"**

✅ Render creará automáticamente:
- Backend API (Web Service)
- Frontend (Static Site)
- Disco persistente de 1GB

---

## Opción 2: Despliegue manual (paso a paso)

### A. Desplegar el Backend

1. **New +** → **Web Service**
2. **Conectar repositorio** de GitHub
3. **Configuración:**
   - **Name:** `reel-ai-backend`
   - **Runtime:** `Python 3`
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Build Command:** `./render_build.sh`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free (o Starter para mejor rendimiento)

4. **Variables de entorno** (Environment):
   ```
   PYTHON_VERSION=3.11.0
   OPENAI_API_KEY=sk-proj-...          # ⚠️ REQUERIDO
   ELEVENLABS_API_KEY=...              # Opcional
   PEXELS_API_KEY=...                  # Opcional
   TEMP_DIR=/tmp/reel_ai
   OUTPUT_DIR=/tmp/reel_ai/output
   CORS_ORIGINS=https://TU-FRONTEND.onrender.com
   ```

5. **Agregar disco persistente:**
   - En la configuración del servicio → **Disks**
   - **Name:** `reel-storage`
   - **Mount Path:** `/tmp/reel_ai`
   - **Size:** 1 GB

6. Click en **"Create Web Service"**

7. **Espera 5-10 minutos** mientras Render:
   - Instala FFmpeg
   - Instala dependencias Python
   - Inicia el servidor

8. **Verifica que funciona:**
   - URL del backend: `https://reel-ai-backend.onrender.com`
   - Prueba: `https://reel-ai-backend.onrender.com/api/health`
   - Deberías ver: `{"status":"ok","apis":{"openai":true,...}}`

---

### B. Desplegar el Frontend

1. **New +** → **Static Site**
2. **Conectar el mismo repositorio**
3. **Configuración:**
   - **Name:** `reel-ai-frontend`
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`

4. **Variables de entorno:**
   ```
   VITE_API_URL=https://reel-ai-backend.onrender.com/api
   ```
   ⚠️ **IMPORTANTE:** Reemplaza con tu URL real del backend

5. Click en **"Create Static Site"**

6. **Espera 3-5 minutos** mientras compila

7. **Tu app estará en:** `https://reel-ai-frontend.onrender.com`

---

## Variables de entorno requeridas

### Backend (obligatorias)

| Variable | Dónde obtenerla | Costo |
|----------|----------------|-------|
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | ~$0.24/reel |

### Backend (opcionales, mejoran calidad)

| Variable | Dónde obtenerla | Costo |
|----------|----------------|-------|
| `ELEVENLABS_API_KEY` | [elevenlabs.io](https://elevenlabs.io) → API Key | ~$0.03/reel |
| `PEXELS_API_KEY` | [pexels.com/api](https://www.pexels.com/api) | Gratis |

### Frontend

| Variable | Valor |
|----------|-------|
| `VITE_API_URL` | `https://TU-BACKEND.onrender.com/api` |

---

## Configurar CORS correctamente

Después de desplegar, actualiza el CORS en el backend:

1. Ve al servicio backend en Render
2. **Environment** → Editar `CORS_ORIGINS`
3. Valor: `https://reel-ai-frontend.onrender.com`
4. **Save Changes** (se reiniciará automáticamente)

---

## Solución de problemas comunes

### ❌ Error: "FFmpeg not found"
**Solución:** Asegúrate de que `render_build.sh` tiene permisos de ejecución:
```bash
chmod +x backend/render_build.sh
git add backend/render_build.sh
git commit -m "Fix build script permissions"
git push
```

### ❌ Error: "CORS policy"
**Solución:** Verifica que `CORS_ORIGINS` en el backend incluye la URL exacta del frontend (con https://)

### ❌ Backend se duerme (plan free)
**Problema:** En el plan gratuito, los servicios se duermen tras 15 min de inactividad.
**Solución:**
- Upgrade a plan Starter ($7/mes) para always-on
- O usa [cron-job.org](https://cron-job.org) para hacer ping cada 10 min

### ❌ Error: "Out of memory"
**Solución:** El plan Free tiene 512MB RAM. Para generar videos:
- Upgrade a Starter (512MB → 2GB)
- O reduce `VIDEO_WIDTH` y `VIDEO_HEIGHT` en `.env`

### ❌ Video tarda más de 5 minutos (timeout)
**Solución:** Render Free tiene timeout de 30s en requests HTTP.
- Esto NO afecta la generación (usa polling, no long-request)
- Si ves errores, verifica que el frontend consulta `/api/status/{job_id}` cada 2s

---

## Costos estimados

### Plan Free (recomendado para empezar)
- ✅ Backend + Frontend: **$0/mes**
- ⚠️ Se duerme tras 15 min sin uso
- ⚠️ 512 MB RAM (puede ser lento)
- ✅ 750 horas/mes incluidas

### Plan Starter (recomendado para producción)
- 💰 Backend: **$7/mes** (always-on, 2GB RAM)
- ✅ Frontend: **$0** (static sites siempre gratis)
- ✅ Sin límite de horas
- ✅ Procesamiento 4× más rápido

### Costos de APIs
- OpenAI (GPT-4o + DALL-E): **~$0.24 por reel**
- ElevenLabs (opcional): **+$0.03 por reel**

**Ejemplo:** 100 reels/mes = $24 de OpenAI + $7 Render = **$31/mes total**

---

## Monitoreo y logs

### Ver logs en tiempo real
1. Dashboard de Render → Tu servicio
2. **Logs** (pestaña superior)
3. Filtra por errores: busca `ERROR` o `Exception`

### Verificar salud del backend
```bash
curl https://TU-BACKEND.onrender.com/api/health
```

Respuesta esperada:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "apis": {
    "openai": true,
    "elevenlabs": false,
    "pexels": false
  }
}
```

---

## Actualizar la aplicación

```bash
# Hacer cambios en el código
git add .
git commit -m "Descripción del cambio"
git push

# Render detecta el push y redespliega automáticamente
```

---

## Dominio personalizado (opcional)

1. En el frontend → **Settings** → **Custom Domain**
2. Agrega tu dominio: `reels.tudominio.com`
3. Configura CNAME en tu DNS:
   ```
   reels.tudominio.com → reel-ai-frontend.onrender.com
   ```
4. Render provee SSL automático (Let's Encrypt)

---

## Mejoras para producción

### 1. Base de datos (historial de reels)
```bash
# Agregar PostgreSQL en Render
New + → PostgreSQL → Conectar al backend
```

### 2. Almacenamiento permanente (AWS S3)
En lugar de `/tmp`, guardar videos en S3:
```python
# backend/.env
AWS_BUCKET_NAME=mi-bucket-reels
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

### 3. Procesamiento paralelo (Celery + Redis)
```bash
# Agregar Redis en Render
New + → Redis → Conectar al backend
```

### 4. Rate limiting
```python
# Instalar slowapi
pip install slowapi
# Limitar a 10 reels/hora por IP
```

---

## Soporte

- **Documentación Render:** [render.com/docs](https://render.com/docs)
- **Status de Render:** [status.render.com](https://status.render.com)
- **Comunidad:** [community.render.com](https://community.render.com)

---

## Checklist final

Antes de compartir tu app:

- [ ] Backend responde en `/api/health`
- [ ] Frontend carga correctamente
- [ ] Generar un reel de prueba funciona end-to-end
- [ ] CORS configurado (sin errores en consola del navegador)
- [ ] API keys configuradas y con créditos
- [ ] Logs del backend sin errores críticos
- [ ] Disco persistente agregado (para no perder videos)

---

¡Listo! Tu aplicación estará en producción en ~15 minutos. 🚀
