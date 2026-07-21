import { motion } from 'framer-motion'
import { HiOutlineArrowRight } from 'react-icons/hi2'

const rankColors = [
  'from-yellow-400 to-amber-500',  // 1st
  'from-gray-300 to-gray-400',     // 2nd
  'from-orange-300 to-orange-400', // 3rd
]

const rankLabels = ['🥇 1st', '🥈 2nd', '🥉 3rd']

export default function CareerScoreCard({ career, rank, explanation, onViewRecs, isSelected }) {
  const pct = Math.round(career.percentage || 0)

  return (
    <motion.div
      whileHover={{ y: -4 }}
      className={`glass-card p-5 transition-all ${isSelected ? 'ring-2 ring-primary-500 shadow-lg' : ''}`}
    >
      {/* Rank badge */}
      <div className="flex items-center justify-between mb-3">
        <span className={`text-xs font-bold px-2 py-1 rounded-full bg-gradient-to-r ${rankColors[rank - 1]} text-white`}>
          {rankLabels[rank - 1]}
        </span>
        <span className="text-2xl font-bold text-primary-600">{pct}%</span>
      </div>

      {/* Career name */}
      <h3 className="text-lg font-semibold mb-1">{career.career_name}</h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">{career.description}</p>

      {/* Skills */}
      {career.skills?.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {career.skills.slice(0, 4).map((skill, i) => (
            <span key={i} className="text-xs bg-primary-50 dark:bg-primary-950/50 text-primary-600 px-2 py-0.5 rounded-full">
              {skill}
            </span>
          ))}
        </div>
      )}

      {/* AI Explanation snippet */}
      {explanation?.explanation && (
        <p className="text-xs text-gray-600 dark:text-gray-300 mb-3 line-clamp-2">{explanation.explanation}</p>
      )}

      {/* View recommendations button */}
      <button
        onClick={onViewRecs}
        className={`w-full text-sm font-medium flex items-center justify-center gap-1 py-2 rounded-lg transition-colors ${
          isSelected
            ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
        }`}
      >
        {isSelected ? 'Hide Resources' : 'View Resources'}
        <HiOutlineArrowRight className="w-3 h-3" />
      </button>
    </motion.div>
  )
}
