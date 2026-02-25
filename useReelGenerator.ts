/**
 * Hook personalizado para gestionar el ciclo de vida de la generación de un reel.
 */

import { useState, useCallback, useRef } from 'react'
import { toast } from 'react-hot-toast'
import {
  generateReel,
  pollJobStatus,
  getDownloadUrl,
  getPreviewUrl,
  type ReelRequest,
  type ReelJob,
  type ReelScript,
} from '../services/api'

type GenerationPhase =
  | 'idle'
  | 'submitting'
  | 'generating_script'
  | 'generating_audio'
  | 'generating_images'
  | 'composing_video'
  | 'completed'
  | 'error'

interface UseReelGeneratorReturn {
  phase: GenerationPhase
  progress: number
  statusMessage: string
  script: ReelScript | null
  jobId: string | null
  downloadUrl: string | null
  previewUrl: string | null
  errorMessage: string | null
  generate: (request: ReelRequest) => Promise<void>
  reset: () => void
}

export function useReelGenerator(): UseReelGeneratorReturn {
  const [phase, setPhase] = useState<GenerationPhase>('idle')
  const [progress, setProgress] = useState(0)
  const [statusMessage, setStatusMessage] = useState('')
  const [script, setScript] = useState<ReelScript | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const generate = useCallback(async (request: ReelRequest) => {
    setPhase('submitting')
    setProgress(5)
    setStatusMessage('Enviando solicitud al servidor...')
    setErrorMessage(null)
    setScript(null)
    setDownloadUrl(null)
    setPreviewUrl(null)

    try {
      // 1. Iniciar la generación
      const { job_id } = await generateReel(request)
      setJobId(job_id)
      setProgress(10)
      toast.success('Generación iniciada correctamente')

      // 2. Polling del estado hasta completar
      await pollJobStatus(
        job_id,
        (job: ReelJob) => {
          // Actualizar UI con cada cambio de estado
          setProgress(job.progress)
          setStatusMessage(job.message)

          if (job.script) {
            setScript(job.script)
          }

          // Mapear estado del backend a fase del frontend
          const phaseMap: Record<string, GenerationPhase> = {
            pending: 'submitting',
            generating_script: 'generating_script',
            generating_audio: 'generating_audio',
            generating_images: 'generating_images',
            composing_video: 'composing_video',
            completed: 'completed',
            failed: 'error',
          }
          setPhase(phaseMap[job.status] || 'submitting')
        },
        2000 // Consultar cada 2 segundos
      )

      // 3. Completado: configurar URLs de descarga y preview
      setDownloadUrl(getDownloadUrl(job_id))
      setPreviewUrl(getPreviewUrl(job_id))
      setProgress(100)
      toast.success('¡Reel generado exitosamente! 🎬')

    } catch (err: any) {
      const msg = err?.message || 'Error inesperado durante la generación'
      setPhase('error')
      setErrorMessage(msg)
      setProgress(0)
      toast.error(msg)
    }
  }, [])

  const reset = useCallback(() => {
    setPhase('idle')
    setProgress(0)
    setStatusMessage('')
    setScript(null)
    setJobId(null)
    setDownloadUrl(null)
    setPreviewUrl(null)
    setErrorMessage(null)
  }, [])

  return {
    phase,
    progress,
    statusMessage,
    script,
    jobId,
    downloadUrl,
    previewUrl,
    errorMessage,
    generate,
    reset,
  }
}
