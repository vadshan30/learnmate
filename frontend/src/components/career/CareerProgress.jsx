import { motion } from 'framer-motion'

function formatTime(totalSeconds) {
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

export default function CareerProgress({ current, total, answered, skipped, elapsed }) {
  const remaining = total - answered - skipped
  const progress = ((current + 1) / total) * 100
  const answeredPct = Math.round((answered / total) * 100)
  const avgTimePerQ = answered > 0 ? elapsed / answered : 30
  const estimatedLeft = Math.ceil(remaining * avgTimePerQ)

  return (
    <div className="glass-card p-4 space-y-3">
      {/* Title + percentage */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          Question {current + 1} of {total}
        </span>
        <span className="text-sm font-bold text-primary-600 dark:text-primary-400">
          {answeredPct}%
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full gradient-bg rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
        />
      </div>

      {/* Stats row */}
      <div className="flex items-center gap-4 text-xs">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-gray-600 dark:text-gray-400">Answered:</span>
          <span className="font-semibold text-gray-800 dark:text-gray-200">{answered}</span>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-yellow-400" />
          <span className="text-gray-600 dark:text-gray-400">Skipped:</span>
          <span className="font-semibold text-gray-800 dark:text-gray-200">{skipped}</span>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-gray-300 dark:bg-gray-600" />
          <span className="text-gray-600 dark:text-gray-400">Remaining:</span>
          <span className="font-semibold text-gray-800 dark:text-gray-200">{remaining}</span>
        </span>
      </div>

      {/* Time row */}
      <div className="flex items-center gap-4 text-[11px] text-gray-500 dark:text-gray-400 border-t border-gray-100 dark:border-gray-800 pt-2">
        <span>
          Time Elapsed: <span className="font-mono font-semibold text-gray-700 dark:text-gray-300">{formatTime(elapsed)}</span>
        </span>
        {remaining > 0 && (
          <span>
            Est. Time Left: <span className="font-mono font-semibold text-gray-700 dark:text-gray-300">{formatTime(estimatedLeft)}</span>
          </span>
        )}
      </div>
    </div>
  )
}
