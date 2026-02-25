/**
 * Panel que muestra el progreso de la generación del reel
 * con animaciones y estado en tiempo real.
 */

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText, Mic, Image, Video, CheckCircle, AlertCircle,
  Loader2, Sparkles
} from 'lucide-react'

type GenerationPhase =
  | 'idle'
  | 'submitting'
  | 'generating_script'
  | 'generating_audio'
  | 'generating_images'
  | 'composing_video'
  | 'completed'
  | 'error'

interface ProgressPanelProps {
  phase: GenerationPhase
  progress: number
  statusMessage: string
  errorMessage: string | null
}

interface Step {
  id: GenerationPhase
  label: string
  icon: React.ReactNode
  description: string
}

const STEPS: Step[] = [
  {
    id: 'generating_script',
    label: 'Guion viral',
    icon: <FileText className="w-5 h-5" />,
    description: 'GPT-4 crea tu guion optimizado para engagement',
  },
  {
    id: 'generating_audio',
    label: 'Voz en off',
    icon: <Mic className="w-5 h-5" />,
    description: 'ElevenLabs genera audio realista',
  },
  {
    id: 'generating_images',
    label: 'Escenas visuales',
    icon: <Image className="w-5 h-5" />,
    description: 'DALL-E 3 crea imágenes únicas para cada escena',
  },
  {
    id: 'composing_video',
    label: 'Composición final',
    icon: <Video className="w-5 h-5" />,
    description: 'FFmpeg ensambla todo en formato 9:16',
  },
]

function getStepStatus(
  stepId: GenerationPhase,
  currentPhase: GenerationPhase
): 'pending' | 'active' | 'completed' | 'error' {
  const order = ['submitting', 'generating_script', 'generating_audio', 'generating_images', 'composing_video', 'completed']
  const stepIdx = order.indexOf(stepId)
  const currentIdx = order.indexOf(currentPhase)

  if (currentPhase === 'error') return 'error'
  if (currentIdx > stepIdx) return 'completed'
  if (currentIdx === stepIdx) return 'active'
  return 'pending'
}

export function ProgressPanel({
  phase,
  progress,
  statusMessage,
  errorMessage
}: ProgressPanelProps) {
  if (phase === 'idle') return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="card-dark p-6 space-y-6"
      >
        {/* Header */}
        <div className="flex items-center gap-3">
          {phase === 'error' ? (
            <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0" />
          ) : phase === 'completed' ? (
            <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0" />
          ) : (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <Loader2 className="w-6 h-6 text-brand-400" />
            </motion.div>
          )}

          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-sm">
              {phase === 'error'
                ? 'Error en la generación'
                : phase === 'completed'
                ? '¡Reel listo! 🎬'
                : 'Generando tu reel...'}
            </h3>
            <p className="text-xs text-white/50 truncate mt-0.5">
              {errorMessage || statusMessage}
            </p>
          </div>

          <span className="text-brand-400 font-bold text-lg tabular-nums">
            {progress}%
          </span>
        </div>

        {/* Barra de progreso */}
        <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-brand-500 via-purple-500 to-pink-500"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>

        {/* Pasos del proceso */}
        <div className="space-y-3">
          {STEPS.map((step) => {
            const status = getStepStatus(step.id, phase)

            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-300
                           ${status === 'active'
                             ? 'bg-brand-500/15 border border-brand-500/30'
                             : status === 'completed'
                             ? 'bg-green-500/10 border border-green-500/20'
                             : status === 'error'
                             ? 'bg-red-500/10 border border-red-500/20'
                             : 'bg-white/3 border border-transparent'
                           }`}
              >
                {/* Icono del paso */}
                <div className={`flex-shrink-0 transition-colors duration-300
                                ${status === 'active' ? 'text-brand-400'
                                  : status === 'completed' ? 'text-green-400'
                                  : status === 'error' ? 'text-red-400'
                                  : 'text-white/20'}`}
                >
                  {status === 'completed' ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : status === 'active' ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                    >
                      <Loader2 className="w-5 h-5" />
                    </motion.div>
                  ) : (
                    step.icon
                  )}
                </div>

                {/* Info del paso */}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium transition-colors duration-300
                                ${status === 'active' ? 'text-white'
                                  : status === 'completed' ? 'text-green-400'
                                  : 'text-white/40'}`}
                  >
                    {step.label}
                  </p>
                  {status === 'active' && (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-xs text-brand-400/70 mt-0.5"
                    >
                      {step.description}
                    </motion.p>
                  )}
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Mensaje de error */}
        {phase === 'error' && errorMessage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-4 rounded-xl bg-red-500/10 border border-red-500/30"
          >
            <p className="text-sm text-red-400">{errorMessage}</p>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}
