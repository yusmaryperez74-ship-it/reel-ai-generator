/**
 * Componente de resultado final: reproductor de video y botón de descarga.
 */

import React, { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Download, Play, Pause, RotateCcw, Share2, Instagram } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface VideoResultProps {
  previewUrl: string
  downloadUrl: string
  onReset: () => void
}

export function VideoResult({ previewUrl, downloadUrl, onReset }: VideoResultProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const togglePlay = () => {
    if (!videoRef.current) return
    if (isPlaying) {
      videoRef.current.pause()
    } else {
      videoRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `reel_${Date.now()}.mp4`
    link.click()
    toast.success('Descarga iniciada')
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Mi Reel creado con IA',
          text: 'Creé este reel con Reel AI Generator',
          url: window.location.href,
        })
      } catch {
        // El usuario canceló el share
      }
    } else {
      await navigator.clipboard.writeText(downloadUrl)
      toast.success('URL copiada al portapapeles')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', damping: 20 }}
      className="space-y-6"
    >
      {/* Badge de éxito */}
      <div className="flex items-center justify-center gap-3 py-4 px-6
                     rounded-2xl bg-green-500/10 border border-green-500/30">
        <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse" />
        <p className="text-sm font-semibold text-green-400">
          ¡Tu reel está listo para publicar!
        </p>
      </div>

      {/* Reproductor de video: formato 9:16 (vertical) */}
      <div className="relative mx-auto" style={{ maxWidth: '280px' }}>
        {/* Marco de teléfono */}
        <div className="relative bg-dark-700 rounded-[2.5rem] overflow-hidden border-4
                       border-white/10 shadow-2xl shadow-brand-500/20"
             style={{ aspectRatio: '9/16' }}>

          <video
            ref={videoRef}
            src={previewUrl}
            className="w-full h-full object-cover"
            loop
            playsInline
            onEnded={() => setIsPlaying(false)}
          />

          {/* Overlay de play/pause */}
          <button
            onClick={togglePlay}
            className="absolute inset-0 flex items-center justify-center
                      bg-black/20 hover:bg-black/30 transition-colors duration-200"
          >
            <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm
                           flex items-center justify-center border border-white/30
                           hover:bg-white/30 transition-all duration-200">
              {isPlaying ? (
                <Pause className="w-7 h-7 text-white" />
              ) : (
                <Play className="w-7 h-7 text-white ml-1" />
              )}
            </div>
          </button>

          {/* Overlay de Instagram con indicadores */}
          <div className="absolute bottom-0 left-0 right-0 p-4 pointer-events-none
                         bg-gradient-to-t from-black/60 to-transparent">
            <div className="flex items-end justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-1.5">
                  <Instagram className="w-4 h-4 text-white" />
                  <span className="text-xs text-white/80 font-medium">Instagram Reel</span>
                </div>
                <div className="w-16 h-1 bg-white/30 rounded-full">
                  <div className="h-full w-1/3 bg-white rounded-full" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Specular effect */}
        <div className="absolute -inset-1 rounded-[2.7rem] bg-gradient-to-br
                       from-brand-500/20 to-purple-500/20 blur-xl -z-10" />
      </div>

      {/* Acciones */}
      <div className="space-y-3">
        {/* Botón principal de descarga */}
        <button
          onClick={handleDownload}
          className="btn-primary w-full"
        >
          <Download className="w-5 h-5" />
          Descargar Reel (MP4)
        </button>

        {/* Acciones secundarias */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={handleShare}
            className="flex items-center justify-center gap-2 py-3 px-4 rounded-2xl
                      bg-white/5 border border-white/10 text-sm text-white/70
                      hover:bg-white/10 hover:text-white transition-all duration-200"
          >
            <Share2 className="w-4 h-4" />
            Compartir
          </button>

          <button
            onClick={onReset}
            className="flex items-center justify-center gap-2 py-3 px-4 rounded-2xl
                      bg-white/5 border border-white/10 text-sm text-white/70
                      hover:bg-white/10 hover:text-white transition-all duration-200"
          >
            <RotateCcw className="w-4 h-4" />
            Nuevo reel
          </button>
        </div>
      </div>

      {/* Consejos para publicar */}
      <div className="p-4 rounded-2xl bg-white/3 border border-white/8 space-y-2">
        <p className="text-xs font-semibold text-white/60 uppercase tracking-wider">
          Tips para máximo alcance
        </p>
        <ul className="space-y-1.5">
          {[
            'Publica entre las 6-9 AM o 6-9 PM',
            'Usa los hashtags generados en la descripción',
            'Añade una pregunta en la descripción para generar comentarios',
            'Responde los primeros 10 comentarios para impulsar el alcance',
          ].map((tip, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-white/50">
              <span className="text-brand-400 mt-0.5">→</span>
              {tip}
            </li>
          ))}
        </ul>
      </div>
    </motion.div>
  )
}
