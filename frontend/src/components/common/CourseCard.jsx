import { motion } from 'framer-motion'
import { HiOutlineClock, HiOutlineCheckCircle, HiOutlinePlus } from 'react-icons/hi2'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

function getLevelBadge(level) {
  const l = String(level || '').toLowerCase()
  if (l.includes('beginner') || l.includes('easy')) return 'badge-green'
  if (l.includes('intermediate') || l.includes('medium')) return 'badge-yellow'
  return 'badge-purple'
}

export default function CourseCard({ item, type = 'course', added = false, onAdd }) {
  const skills = item.skills_gained || item.required_skills || item.skills_covered || []
  const level = item.level || item.difficulty || ''
  const levelStr = typeof level === 'object' ? level.value || '' : level
  const provider = item.provider || item.domain || ''
  const duration = item.duration || item.estimated_time || ''

  return (
    <motion.div variants={fadeUp} whileHover={{ y: -3 }} className="glass-card p-5 flex flex-col">
      <div className="flex items-start justify-between gap-2 mb-3">
        <span className={`badge ${getLevelBadge(levelStr)}`}>
          {levelStr || type}
        </span>
        {provider && <span className="text-xs text-gray-400">{provider}</span>}
      </div>
      <h3 className="font-semibold mb-2 line-clamp-2">{item.title || item.name}</h3>
      {item.description && (
        <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">{item.description}</p>
      )}
      {duration && (
        <div className="flex items-center gap-1 text-xs text-gray-400 mb-3">
          <HiOutlineClock className="w-3.5 h-3.5" />
          {duration}
        </div>
      )}
      <div className="mt-auto">
        {skills.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {skills.slice(0, 4).map((s, i) => (
              <span key={i} className="text-[11px] px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">{s}</span>
            ))}
            {skills.length > 4 && (
              <span className="text-[11px] px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-400">+{skills.length - 4}</span>
            )}
          </div>
        )}
        {onAdd && (
          <button
            onClick={() => onAdd(item)}
            disabled={added}
            className={`w-full text-sm py-2 rounded-lg font-medium transition-all flex items-center justify-center gap-1.5 ${
              added
                ? 'bg-green-100 dark:bg-green-900/30 text-green-600 cursor-default'
                : 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 hover:bg-primary-100 dark:hover:bg-primary-900/50'
            }`}
          >
            {added ? (
              <><HiOutlineCheckCircle className="w-4 h-4" /> Already Added</>
            ) : (
              <><HiOutlinePlus className="w-4 h-4" /> Add to Roadmap</>
            )}
          </button>
        )}
      </div>
    </motion.div>
  )
}
