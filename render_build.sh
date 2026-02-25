#!/usr/bin/env bash
# ============================================================
# Script de build para Render (Backend)
# ============================================================

set -o errexit  # Salir si hay error

echo "📦 Instalando FFmpeg..."
apt-get update
apt-get install -y ffmpeg

echo "🐍 Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build completado"
