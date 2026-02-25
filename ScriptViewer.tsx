/**
 * Componente para mostrar el guion generado por IA.
 * Muestra el hook, escenas y hashtags del reel.
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { FileText, Hash, ChevronDown, ChevronUp, Eye } from 'lucide-react'
import type { ReelScript } from '../services/api'

interface ScriptViewerProps {
  script: ReelScript
}

export function ScriptViewer({ script }: ScriptViewerProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-dark overflow-hidden"
    >
      {/* Header colapsable */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-5
                   hover:bg-white/3 transition-colors duration-200"
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brand-500/20 flex items-center justify-center">
            <FileText className="w-5 h-5 text-brand-400" />
          </div>
          <div className="text-left">
            <h3 className="font-semibold text-sm">{script.title}</h3>
            <p className="text-xs text-white/40 mt-0.5">
              {script.scenes.length} escenas · {Math.round(script.total_duration)}s
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-white/40">
          <Eye className="w-4 h-4" />
          <span className="text-xs">{expanded ? 'Ocultar' : 'Ver guion'}</span>
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Contenido colapsable */}
      {expanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          className="border-t border-white/5 p-5 space-y-4"
        >
          {/* Hook */}
          <div className="p-4 rounded-2xl bg-gradient-to-r from-brand-500/15 to-purple-500/15
                         border border-brand-500/30">
            <p className="text-xs text-brand-400 font-medium mb-2">HOOK (Primer 3 segundos)</p>
            <p className="text-sm text-white font-semibold">"{script.hook}"</p>
          </div>

          {/* Escenas */}
          <div className="space-y-3">
            <p className="text-xs text-white/40 font-medium uppercase tracking-wider">Escenas</p>
            {script.scenes.map((scene, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex gap-3"
              >
                <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-white/10
                               flex items-center justify-center text-xs font-bold text-white/60">
                  {scene.order}
                </div>
                <div className="flex-1 space-y-1.5">
                  <p className="text-sm text-white/90">{scene.text}</p>
                  <p className="text-xs text-white/30 italic">
                    Visual: {scene.visual_prompt}
                  </p>
                  <span className="text-xs text-white/25">{scene.duration}s</span>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Call to Action */}
          <div className="p-3 rounded-xl bg-white/5 border border-white/10">
            <p className="text-xs text-white/40 mb-1">CALL TO ACTION</p>
            <p className="text-sm text-white/80">{script.call_to_action}</p>
          </div>

          {/* Hashtags */}
          <div className="space-y-2">
            <div className="flex items-center gap-1.5">
              <Hash className="w-3.5 h-3.5 text-white/40" />
              <p className="text-xs text-white/40 font-medium">Hashtags sugeridos</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {script.hashtags.map((tag, i) => (
                <span
                  key={i}
                  className="text-xs px-3 py-1.5 rounded-xl bg-brand-500/15
                             border border-brand-500/30 text-brand-400"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
