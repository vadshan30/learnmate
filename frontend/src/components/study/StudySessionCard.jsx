import { motion } from 'framer-motion'
import { HiOutlineClock, HiOutlineCheckCircle, HiOutlinePlay, HiOutlineTrash, HiOutlineEllipsisVertical } from 'react-icons/hi2'

const STATUS_CONFIG = {
  scheduled: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-300', label: 'Scheduled' },
  in_progress: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-300', label: 'In Progress' },
  completed: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-300', label: 'Completed' },
  skipped: { bg: 'bg-purple-100 dark:bg-purple-900/30', text: 'text-purple-700 dark:text-purple-300', label: 'Skipped' },
  missed: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-300', label: 'Missed' },
}

const PRIORITY_DOT = {
  low: 'bg-green-500',
  medium: 'bg-yellow-500',
  high: 'bg-red-500',
}

export default function StudySessionCard({ session, onComplete, onDelete, onEdit }) {
  const status = STATUS_CONFIG[session.status] || STATUS_CONFIG.scheduled
  const isCompleted = session.status === 'completed'

  return (
    <motion.div
      layout
      whileHover={{ scale: 1.01 }}
      className={`glass-card p-4 transition-all ${isCompleted ? 'opacity-70' : ''}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <div className={`w-2 h-2 rounded-full ${PRIORITY_DOT[session.priority] || PRIORITY_DOT.medium}`} />
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${status.bg} ${status.text}`}>
              {status.label}
            </span>
          </div>
          <h4 className={`font-medium text-sm truncate ${isCompleted ? 'line-through text-gray-400' : ''}`}>
            {session.title}
          </h4>
          {session.topic && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">{session.topic}</p>
          )}
          <div className="flex items-center gap-2 mt-2 text-xs text-gray-500 dark:text-gray-400">
            <HiOutlineClock className="w-3.5 h-3.5" />
            <span>{session.start_time} - {session.end_time}</span>
            <span className="text-gray-300 dark:text-gray-600">|</span>
            <span>{session.duration}h</span>
          </div>
        </div>
        <div className="flex flex-col gap-1">
          {!isCompleted && (
            <button
              onClick={() => onComplete?.(session.id)}
              className="p-1.5 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 text-green-600 transition-colors"
              title="Mark complete"
            >
              <HiOutlineCheckCircle className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={() => onEdit?.(session)}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition-colors"
            title="Edit"
          >
            <HiOutlineEllipsisVertical className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete?.(session.id)}
            className="p-1.5 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-500 transition-colors"
            title="Delete"
          >
            <HiOutlineTrash className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  )
}
