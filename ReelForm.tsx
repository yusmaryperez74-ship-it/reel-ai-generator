/**
 * Formulario principal para configurar y crear el reel.
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Sparkles, Mic, Image, Music, Clock, Languages,
  Subtitles, ChevronDown, Zap
} from 'lucide-react'
import type { ReelRequest, VideoStyle, VoiceGender, MusicGenre } from '../services/api'

interface ReelFormProps {
  onSubmit: (request: ReelRequest) => void
  isLoading: boolean
}

// Opciones de configuración del reel
const STYLES: { value: VideoStyle; label: string; emoji: string }[] = [
  { value: 'vibrant', label: 'Vibrante', emoji: '🌈' },
  { value: 'cinematic', label: 'Cinematográfico', emoji: '🎬' },
  { value: 'minimal', label: 'Minimalista', emoji: '⬜' },
  { value: 'dark', label: 'Oscuro', emoji: '🌑' },
]

const MUSIC_OPTIONS: { value: MusicGenre; label: string; emoji: string }[] = [
  { value: 'upbeat', label: 'Energético', emoji: '⚡' },
  { value: 'motivational', label: 'Motivacional', emoji: '💪' },
  { value: 'ambient', label: 'Ambiental', emoji: '🌊' },
  { value: 'dramatic', label: 'Dramático', emoji: '🎭' },
  { value: 'none', label: 'Sin música', emoji: '🔇' },
]

const TOPIC_SUGGESTIONS = [
  '5 hábitos que cambiarán tu vida para siempre',
  'Cómo ganar dinero mientras duermes',
  'El secreto que nadie te enseña sobre el dinero',
  '3 ejercicios para un cuerpo perfecto en 10 minutos',
  'Por qué el 99% de la gente falla en sus metas',
]

export function ReelForm({ onSubmit, isLoading }: ReelFormProps) {
  const [topic, setTopic] = useState('')
  const [language, setLanguage] = useState('es')
  const [style, setStyle] = useState<VideoStyle>('vibrant')
  const [voiceGender, setVoiceGender] = useState<VoiceGender>('female')
  const [music, setMusic] = useState<MusicGenre>('upbeat')
  const [duration, setDuration] = useState(30)
  const [addSubtitles, setAddSubtitles] = useState(true)
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim()) return

    onSubmit({
      topic: topic.trim(),
      language,
      style,
      voice_gender: voiceGender,
      music,
      duration_seconds: duration,
      add_subtitles: addSubtitles,
    })
  }

  const useSuggestion = (suggestion: string) => {
    setTopic(suggestion)
  }

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit}
      className="space-y-6"
    >
      {/* Campo principal: Tema del reel */}
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm font-medium text-white/80">
          <Sparkles className="w-4 h-4 text-brand-400" />
          Tema de tu reel
        </label>

        <textarea
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Ej: 5 secretos para ahorrar dinero que los ricos no quieren que sepas..."
          className="input-dark resize-none h-28 text-base leading-relaxed"
          maxLength={500}
          disabled={isLoading}
        />

        <div className="flex justify-between items-center text-xs text-white/40">
          <span>Sé específico para mejores resultados</span>
          <span>{topic.length}/500</span>
        </div>

        {/* Sugerencias de temas */}
        <div className="space-y-1.5">
          <p className="text-xs text-white/40">Ideas virales:</p>
          <div className="flex flex-wrap gap-2">
            {TOPIC_SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                type="button"
                onClick={() => useSuggestion(s)}
                disabled={isLoading}
                className="text-xs px-3 py-1.5 rounded-xl bg-white/5 hover:bg-brand-500/20
                           border border-white/10 hover:border-brand-500/40
                           text-white/60 hover:text-white transition-all duration-200
                           disabled:opacity-40 truncate max-w-[200px]"
                title={s}
              >
                {s.length > 35 ? s.slice(0, 35) + '…' : s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Selector de estilo visual */}
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm font-medium text-white/80">
          <Image className="w-4 h-4 text-brand-400" />
          Estilo visual
        </label>
        <div className="grid grid-cols-4 gap-2">
          {STYLES.map(({ value, label, emoji }) => (
            <button
              key={value}
              type="button"
              onClick={() => setStyle(value)}
              disabled={isLoading}
              className={`flex flex-col items-center gap-1.5 p-3 rounded-2xl border
                         transition-all duration-200 text-sm font-medium
                         ${style === value
                           ? 'border-brand-500 bg-brand-500/20 text-white'
                           : 'border-white/10 bg-white/5 text-white/60 hover:border-white/20'
                         }`}
            >
              <span className="text-xl">{emoji}</span>
              <span className="text-xs">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Duración */}
      <div className="space-y-3">
        <label className="flex items-center justify-between text-sm font-medium text-white/80">
          <span className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-brand-400" />
            Duración del reel
          </span>
          <span className="text-brand-400 font-bold">{duration}s</span>
        </label>
        <div className="relative">
          <input
            type="range"
            min={15}
            max={60}
            step={5}
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            disabled={isLoading}
            className="w-full accent-brand-500 cursor-pointer"
          />
          <div className="flex justify-between text-xs text-white/30 mt-1">
            <span>15s</span>
            <span>30s</span>
            <span>45s</span>
            <span>60s</span>
          </div>
        </div>
      </div>

      {/* Configuración avanzada (colapsable) */}
      <div className="border border-white/10 rounded-2xl overflow-hidden">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full flex items-center justify-between p-4 text-sm text-white/60
                     hover:text-white hover:bg-white/5 transition-all duration-200"
        >
          <span className="flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Opciones avanzadas
          </span>
          <ChevronDown
            className={`w-4 h-4 transition-transform duration-200 ${showAdvanced ? 'rotate-180' : ''}`}
          />
        </button>

        {showAdvanced && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            className="p-4 pt-0 space-y-4 border-t border-white/10"
          >
            {/* Voz */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-xs font-medium text-white/60">
                <Mic className="w-3.5 h-3.5" />
                Voz en off
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { value: 'female' as VoiceGender, label: '👩 Femenina' },
                  { value: 'male' as VoiceGender, label: '👨 Masculina' },
                ].map(({ value, label }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setVoiceGender(value)}
                    disabled={isLoading}
                    className={`p-2.5 rounded-xl border text-sm transition-all duration-200
                               ${voiceGender === value
                                 ? 'border-brand-500 bg-brand-500/20 text-white'
                                 : 'border-white/10 bg-white/5 text-white/50 hover:border-white/20'
                               }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Música */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-xs font-medium text-white/60">
                <Music className="w-3.5 h-3.5" />
                Música de fondo
              </label>
              <div className="grid grid-cols-3 gap-2">
                {MUSIC_OPTIONS.map(({ value, label, emoji }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setMusic(value)}
                    disabled={isLoading}
                    className={`flex items-center gap-1.5 p-2 rounded-xl border text-xs
                               transition-all duration-200 justify-center
                               ${music === value
                                 ? 'border-brand-500 bg-brand-500/20 text-white'
                                 : 'border-white/10 bg-white/5 text-white/50 hover:border-white/20'
                               }`}
                  >
                    {emoji} {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Subtítulos y Idioma */}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-xs font-medium text-white/60 cursor-pointer">
                <Subtitles className="w-3.5 h-3.5" />
                Subtítulos estilo TikTok
              </label>
              <button
                type="button"
                onClick={() => setAddSubtitles(!addSubtitles)}
                disabled={isLoading}
                className={`relative w-11 h-6 rounded-full transition-colors duration-200
                           ${addSubtitles ? 'bg-brand-500' : 'bg-white/20'}`}
              >
                <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white
                                  shadow-sm transition-transform duration-200
                                  ${addSubtitles ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>

            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 text-xs font-medium text-white/60">
                <Languages className="w-3.5 h-3.5" />
                Idioma
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                disabled={isLoading}
                className="input-dark py-2 text-xs flex-1"
              >
                <option value="es">🇪🇸 Español</option>
                <option value="en">🇺🇸 English</option>
              </select>
            </div>
          </motion.div>
        )}
      </div>

      {/* Botón de generación */}
      <button
        type="submit"
        disabled={isLoading || !topic.trim()}
        className="btn-primary w-full text-base py-5"
      >
        {isLoading ? (
          <>
            <span className="spinner w-5 h-5" />
            Generando tu reel...
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            Crear Reel con IA
          </>
        )}
      </button>
    </motion.form>
  )
}
