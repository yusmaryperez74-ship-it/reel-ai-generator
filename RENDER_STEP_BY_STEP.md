# 📸 Render: Guía paso a paso con capturas

Esta guía te lleva de la mano para desplegar en Render SIN errores.

---

## ANTES DE EMPEZAR

### ✅ Checklist

- [ ] Tienes cuenta en GitHub (gratis en github.com)
- [ ] Tienes cuenta en Render (gratis en render.com)
- [ ] Tienes API key de OpenAI (platform.openai.com/api-keys)
- [ ] Código descargado y descomprimido

---

## PASO 1: Subir código a GitHub

### 1.1 Crear repositorio en GitHub

1. Ve a [github.com](https://github.com)
2. Click en **"+"** (arriba derecha) → **"New repository"**
3. Nombre: `reel-ai-generator`
4. Visibilidad: **Public** (o Private si tienes plan de pago)
5. ❌ **NO marques** "Add README" ni ".gitignore" ni "license"
6. Click en **"Create repository"**
7. **Copia la URL** que aparece (ej: `https://github.com/tu-user/reel-ai-generator.git`)

### 1.2 Subir tu código

Abre la terminal en la carpeta del proyecto:

```bash
cd reel-ai-generator

# Inicializar git
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Initial commit: Reel AI Generator"

# Conectar con GitHub (pega TU URL del paso 1.1)
git remote add origin https://github.com/TU-USUARIO/reel-ai-generator.git

# Subir código
git branch -M main
git push -u origin main
```

**Si te pide usuario/contraseña:**
- Usuario: tu username de GitHub
- Contraseña: crea un **Personal Access Token** en:
  - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Generate new token → Marca "repo" → Generate → Copia el token
  - Usa ese token como contraseña

✅ **Verifica:** Recarga la página de GitHub, debes ver todos tus archivos ahí.

---

## PASO 2: Desplegar Backend en Render

### 2.1 Crear Web Service

1. Ve a [render.com](https://render.com) y haz login
2. Click en **"New +"** (arriba derecha)
3. Selecciona **"Web Service"**

### 2.2 Conectar GitHub

1. Click en **"Connect a repository"**
2. Si es tu primera vez: **"Connect GitHub"** → Autorizar Render
3. Busca `reel-ai-generator` en la lista
4. Click en **"Connect"**

### 2.3 Configurar el servicio

**Pantalla de configuración:**

| Campo | Valor |
|-------|-------|
| **Name** | `reel-ai-backend` |
| **Region** | Choose the region closest to you (ej: Oregon USA) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `./render_build.sh` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` (para empezar) |

### 2.4 Variables de entorno

Scroll hasta **"Environment Variables"** y agrega:

Click en **"Add Environment Variable"** para cada una:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `OPENAI_API_KEY` | `sk-proj-TU_KEY_COMPLETA_AQUI` ⚠️ |
| `TEMP_DIR` | `/tmp/reel_ai` |
| `OUTPUT_DIR` | `/tmp/reel_ai/output` |

**Opcional (mejoran calidad pero no son necesarios):**
| Key | Value |
|-----|-------|
| `ELEVENLABS_API_KEY` | `tu_key_elevenlabs` |
| `PEXELS_API_KEY` | `tu_key_pexels` |

⚠️ **IMPORTANTE:** La `OPENAI_API_KEY` debe empezar con `sk-proj-` o `sk-`

### 2.5 Agregar disco persistente

Scroll hasta **"Disks"** → Click en **"Add Disk"**

| Campo | Valor |
|-------|-------|
| **Name** | `reel-storage` |
| **Mount Path** | `/tmp/reel_ai` |
| **Size** | `1 GB` (gratis) |

### 2.6 Crear servicio

1. Scroll hasta abajo
2. Click en **"Create Web Service"**
3. **Espera 5-10 minutos** mientras Render:
   - Clona tu repositorio
   - Instala FFmpeg
   - Instala Python y dependencias
   - Inicia el servidor

**Progreso:** Verás logs en tiempo real. Busca estos mensajes:
```
==> Installing FFmpeg...
==> Installing dependencies from requirements.txt
==> Starting server on port 10000
🎬 REEL AI GENERATOR - Iniciando servidor...
   OpenAI: ✅
==> Your service is live 🎉
```

### 2.7 Verificar backend

1. Copia la URL de tu servicio (arriba, algo como `https://reel-ai-backend.onrender.com`)
2. Abre en el navegador: `https://TU-URL.onrender.com/api/health`
3. Debes ver algo como:
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

✅ Si ves `"openai": true` → Backend funciona correctamente

❌ Si ves `"openai": false` → Revisa tu API key en Environment Variables

---

## PASO 3: Desplegar Frontend en Render

### 3.1 Crear Static Site

1. En Render dashboard, click en **"New +"** → **"Static Site"**
2. Selecciona **el mismo repositorio** (`reel-ai-generator`)
3. Click en **"Connect"**

### 3.2 Configurar el sitio

| Campo | Valor |
|-------|-------|
| **Name** | `reel-ai-frontend` |
| **Branch** | `main` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

### 3.3 Variable de entorno

En **"Environment Variables"** → **"Add Environment Variable"**:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://reel-ai-backend.onrender.com/api` |

⚠️ **REEMPLAZA** `reel-ai-backend` con el nombre exacto de tu backend del Paso 2

### 3.4 Crear sitio

1. Click en **"Create Static Site"**
2. **Espera 3-5 minutos** mientras:
   - Instala Node.js
   - Instala dependencias (React, Vite, etc.)
   - Compila el proyecto
   - Publica archivos estáticos

Logs esperados:
```
==> Installing dependencies...
==> Running npm run build
==> Build complete
==> Your site is live 🎉
```

### 3.5 Verificar frontend

1. Copia la URL (ej: `https://reel-ai-frontend.onrender.com`)
2. Ábrela en el navegador
3. Debes ver la interfaz de Reel AI Generator

---

## PASO 4: Configurar CORS (crítico)

El frontend y backend ahora están en URLs diferentes, necesitas habilitar CORS:

1. Ve al servicio **Backend** en Render
2. **Environment** (menú izquierdo)
3. Click en **"Add Environment Variable"**
4. Agregar:

| Key | Value |
|-----|-------|
| `CORS_ORIGINS` | `https://reel-ai-frontend.onrender.com` |

⚠️ Usa la URL EXACTA de tu frontend (la del paso 3.5)

5. Click en **"Save Changes"**
6. El backend se reiniciará automáticamente (~30 segundos)

---

## PASO 5: Probar la aplicación completa

1. Abre tu frontend: `https://reel-ai-frontend.onrender.com`
2. En el formulario, escribe un tema de prueba:
   - Ejemplo: "3 tips para ser más productivo"
3. Deja las opciones por defecto
4. Click en **"Crear Reel con IA"**
5. **Espera 2-4 minutos** (primera vez puede tardar más)
6. Verás el progreso en tiempo real:
   - ✅ Guion viral
   - ✅ Voz en off
   - ✅ Escenas visuales
   - ✅ Composición final
7. Cuando termine, click en **"Descargar Reel (MP4)"**

✅ **Si descargó el video:** Todo funciona correctamente

---

## SOLUCIÓN DE PROBLEMAS

### ❌ Backend muestra "Build failed"

**Problema:** No encontró `render_build.sh` o no tiene permisos

**Solución:**
```bash
chmod +x backend/render_build.sh
git add backend/render_build.sh
git commit -m "Fix build script"
git push
```

Render detectará el push y volverá a intentar automáticamente.

---

### ❌ Frontend muestra pantalla blanca

**Problema:** Error en la compilación o variable de entorno incorrecta

**Solución:**
1. Ve a los **Logs** del frontend en Render
2. Busca errores en la compilación
3. Verifica que `VITE_API_URL` tiene la URL correcta del backend
4. Si cambias algo, Render redespliega automáticamente

---

### ❌ Error CORS en el navegador

**Problema:** Frontend no puede conectarse al backend

**Abrir consola del navegador (F12) y verás:**
```
Access to fetch at 'https://...' has been blocked by CORS policy
```

**Solución:**
1. Ve al backend en Render → **Environment**
2. Verifica que `CORS_ORIGINS` tiene la URL exacta del frontend
3. Debe incluir `https://` y NO terminar en `/`
4. Guarda cambios y espera que reinicie

---

### ❌ "OpenAI API key not valid"

**Problema:** API key incorrecta o sin créditos

**Solución:**
1. Ve a [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Verifica que la key es válida (no expirada)
3. Ve a [platform.openai.com/usage](https://platform.openai.com/usage)
4. Verifica que tienes créditos disponibles ($5 mínimo recomendado)
5. Copia la key completa (incluye el `sk-`)
6. Actualiza en Render → Backend → Environment → `OPENAI_API_KEY`

---

### ❌ Backend se duerme (plan free)

**Problema:** Tras 15 min sin uso, Render duerme los servicios gratuitos

**Síntomas:** Primera request tarda 30-60 segundos

**Soluciones:**
- **Opción 1 (gratis):** Usar [cron-job.org](https://cron-job.org) para hacer ping cada 10 min
- **Opción 2 ($7/mes):** Upgrade a plan Starter → Always-on

---

### ❌ Video sin audio o imágenes negras

**Problema:** Servicios de IA fallaron

**Solución:**
1. Ve a Render → Backend → **Logs**
2. Busca mensajes de error con `[TTS]` o `[ImageGen]`
3. Causas comunes:
   - Sin créditos en OpenAI
   - Límite de rate de API excedido
   - Red inestable (reintentar)

---

## MEJORAS POSTERIORES

### Upgrade a Starter ($7/mes)

**Beneficios:**
- Always-on (no se duerme)
- 512 MB → 2 GB RAM (4× más rápido)
- Mejor para producción

**Cómo:**
1. Backend → **Settings** → **Instance Type**
2. Cambiar de "Free" a "Starter"
3. Confirm

### Agregar dominio personalizado

1. Frontend → **Settings** → **Custom Domain**
2. Agrega: `reels.tudominio.com`
3. Configura CNAME en tu DNS:
```
reels.tudominio.com → reel-ai-frontend.onrender.com
```
4. SSL automático en 5-10 min

### Monitorear costos

- **Render:** Dashboard muestra uso mensual
- **OpenAI:** [platform.openai.com/usage](https://platform.openai.com/usage)

---

## RESUMEN

✅ **Backend:** https://reel-ai-backend.onrender.com
✅ **Frontend:** https://reel-ai-frontend.onrender.com
✅ **Docs API:** https://reel-ai-backend.onrender.com/docs

**Tiempo total de despliegue:** ~15 minutos
**Costo:** $0/mes (plan free) + ~$0.24 por cada reel generado

---

¡Tu aplicación está en producción! 🎉

Comparte la URL del frontend con amigos para que prueben.
