/**
 * Componente raíz de la aplicación Reel AI Generator.
 * Layout principal con formulario, progreso y resultado.
 */

import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Zap, Github, Instagram } from 'lucide-react'
import { ReelForm } from './components/ReelForm'
import { ProgressPanel } from './components/ProgressPanel'
import { ScriptViewer } from './components/ScriptViewer'
import { VideoResult } from './components/VideoResult'
import { useReelGenerator } from './hooks/useReelGenerator'
import { checkHealth, type HealthStatus } from './services/api'

export default function App() {
  const {
    phase,
    progress,
    statusMessage,
    script,
    downloadUrl,
    previewUrl,
    errorMessage,
    generate,
    reset,
  } = useReelGenerator()

  const [health, setHealth] = useState<HealthStatus | null>(null)
  const isLoading = !['idle', 'completed', 'error'].includes(phase)

  // Verificar estado del servidor al cargar
  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth(null))
  }, [])

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-dark-900/80 backdrop-blur-xl
                         border-b border-white/5">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-brand flex items-center justify-center
                           shadow-lg shadow-brand-500/40">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-sm tracking-tight">Reel AI Generator</h1>
              <p className="text-xs text-white/40">Powered by GPT-4 + DALL-E 3</p>
            </div>
          </div>

          {/* Estado del servidor */}
          <div className="flex items-center gap-2">
            {health && (
              <div className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-xl
                             ${health.apis.openai
                               ? 'bg-green-500/15 border border-green-500/30 text-green-400'
                               : 'bg-red-500/15 border border-red-500/30 text-red-400'
                             }`}>
                <div className={`w-1.5 h-1.5 rounded-full
                               ${health.apis.openai ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
                {health.apis.openai ? 'APIs OK' : 'Sin API Key'}
              </div>
            )}

            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10
                        text-white/40 hover:text-white transition-all duration-200"
            >
              <Github className="w-4 h-4" />
            </a>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="text-center py-16 px-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4 max-w-2xl mx-auto"
        >
          {/* Badge */}
          <div className="inline-flex items-center gap-2 text-xs px-4 py-2 rounded-full
                         bg-brand-500/15 border border-brand-500/30 text-brand-400">
            <Zap className="w-3.5 h-3.5" />
            <span>Genera reels virales en minutos con IA</span>
          </div>

          {/* Título principal */}
          <h2 className="text-4xl sm:text-5xl font-black leading-tight">
            Crea{' '}
            <span className="text-gradient">Reels Virales</span>
            <br />
            con Inteligencia Artificial
          </h2>

          <p className="text-base text-white/50 max-w-lg mx-auto">
            Solo escribe el tema. La IA genera el guion, la voz en off, las imágenes,
            los subtítulos y exporta en formato 9:16 listo para Instagram.
          </p>

          {/* Features */}
          <div className="flex flex-wrap justify-center gap-3 pt-2">
            {['Guion viral', 'Voz IA', 'Imágenes DALL-E', 'Subtítulos TikTok', 'Formato 9:16'].map((f) => (
              <span key={f} className="text-xs px-3 py-1.5 rounded-xl bg-white/5
                                      border border-white/10 text-white/50">
                ✓ {f}
              </span>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Contenido principal */}
      <main className="max-w-5xl mx-auto px-4 pb-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Columna izquierda: Formulario y progreso */}
          <div className="space-y-6">
            {/* Formulario (visible cuando no se está procesando o hay error) */}
            <AnimatePresence mode="wait">
              {(phase === 'idle' || phase === 'error') && (
                <motion.div
                  key="form"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="card-dark p-6"
                >
                  <h3 className="font-bold text-lg mb-6 flex items-center gap-2">
                    <Instagram className="w-5 h-5 text-brand-400" />
                    Configurar mi reel
                  </h3>
                  <ReelForm onSubmit={generate} isLoading={isLoading} />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Panel de progreso */}
            <AnimatePresence>
              {phase !== 'idle' && phase !== 'completed' && (
                <ProgressPanel
                  phase={phase}
                  progress={progress}
                  statusMessage={statusMessage}
                  errorMessage={errorMessage}
                />
              )}
            </AnimatePresence>

            {/* Botón para crear otro reel en caso de error */}
            {phase === 'error' && (
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                onClick={reset}
                className="w-full py-3 rounded-2xl border border-white/15
                          text-sm text-white/60 hover:text-white hover:bg-white/5
                          transition-all duration-200"
              >
                ← Intentar de nuevo
              </motion.button>
            )}
          </div>

          {/* Columna derecha: Script y resultado */}
          <div className="space-y-6">
            {/* Guion generado */}
            <AnimatePresence>
              {script && (
                <ScriptViewer key="script" script={script} />
              )}
            </AnimatePresence>

            {/* Resultado del video */}
            <AnimatePresence>
              {phase === 'completed' && downloadUrl && previewUrl && (
                <VideoResult
                  key="result"
                  previewUrl={previewUrl}
                  downloadUrl={downloadUrl}
                  onReset={reset}
                />
              )}
            </AnimatePresence>

            {/* Placeholder cuando no hay contenido */}
            {phase === 'idle' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="card-dark p-8 flex flex-col items-center justify-center
                          text-center space-y-4 min-h-[300px]"
              >
                <div className="w-20 h-20 rounded-3xl bg-gradient-brand flex items-center
                               justify-center shadow-xl shadow-brand-500/30 animate-float">
                  <Sparkles className="w-10 h-10 text-white" />
                </div>
                <h3 className="font-semibold text-white/80">Tu reel aparecerá aquí</h3>
                <p className="text-sm text-white/40 max-w-xs">
                  Escribe el tema de tu reel en el formulario y la IA hará el resto
                </p>
              </motion.div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 py-6 text-center">
        <p className="text-xs text-white/25">
          Reel AI Generator · Powered by OpenAI GPT-4, DALL-E 3 & ElevenLabs
        </p>
      </footer>
    </div>
  )
}
