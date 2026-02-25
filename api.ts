/**
 * Cliente API para comunicarse con el backend FastAPI.
 */

import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 300_000, // 5 minutos (generación puede tardar)
})

// ---- Tipos de datos ----

export type VideoStyle = 'cinematic' | 'vibrant' | 'minimal' | 'dark'
export type VoiceGender = 'male' | 'female'
export type MusicGenre = 'none' | 'upbeat' | 'ambient' | 'dramatic' | 'motivational'

export interface ReelRequest {
  topic: string
  language: string
  style: VideoStyle
  voice_gender: VoiceGender
  music: MusicGenre
  duration_seconds: number
  add_subtitles: boolean
}

export interface ScriptScene {
  order: number
  text: string
  visual_prompt: string
  duration: number
  transition: string
}

export interface ReelScript {
  title: string
  hook: string
  scenes: ScriptScene[]
  call_to_action: string
  hashtags: string[]
  total_duration: number
}

export type JobStatus =
  | 'pending'
  | 'generating_script'
  | 'generating_audio'
  | 'generating_images'
  | 'composing_video'
  | 'completed'
  | 'failed'

export interface ReelJob {
  job_id: string
  status: JobStatus
  progress: number
  message: string
  download_url: string | null
  script: ReelScript | null
  error: string | null
  created_at: string | null
}

export interface HealthStatus {
  status: string
  version: string
  apis: {
    openai: boolean
    elevenlabs: boolean
    stability: boolean
    pexels: boolean
  }
}

// ---- Funciones de API ----

/**
 * Inicia la generación de un nuevo reel.
 */
export async function generateReel(request: ReelRequest): Promise<{ job_id: string; estimated_time_seconds: number }> {
  const response = await api.post('/generate', request)
  return response.data
}

/**
 * Consulta el estado de un trabajo de generación.
 */
export async function getJobStatus(jobId: string): Promise<ReelJob> {
  const response = await api.get(`/status/${jobId}`)
  return response.data
}

/**
 * Retorna la URL de descarga del video.
 */
export function getDownloadUrl(jobId: string): string {
  return `${BASE_URL}/download/${jobId}`
}

/**
 * Retorna la URL de preview del video.
 */
export function getPreviewUrl(jobId: string): string {
  return `${BASE_URL}/preview/${jobId}`
}

/**
 * Verifica el estado de salud del servidor y APIs configuradas.
 */
export async function checkHealth(): Promise<HealthStatus> {
  const response = await api.get('/health')
  return response.data
}

/**
 * Polling del estado de un trabajo hasta que termine.
 * Llama al callback onUpdate con cada actualización.
 */
export async function pollJobStatus(
  jobId: string,
  onUpdate: (job: ReelJob) => void,
  intervalMs: number = 2000
): Promise<ReelJob> {
  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      try {
        const job = await getJobStatus(jobId)
        onUpdate(job)

        if (job.status === 'completed') {
          clearInterval(interval)
          resolve(job)
        } else if (job.status === 'failed') {
          clearInterval(interval)
          reject(new Error(job.error || 'Error desconocido en la generación'))
        }
      } catch (error) {
        clearInterval(interval)
        reject(error)
      }
    }, intervalMs)
  })
}
