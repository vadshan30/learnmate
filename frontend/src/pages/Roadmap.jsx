import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  HiOutlineChevronDown, HiOutlineCheckCircle, HiOutlineClock,
  HiOutlineAcademicCap, HiOutlineRocketLaunch, HiOutlineArrowPath,
  HiOutlineTrash, HiOutlineMap,
} from 'react-icons/hi2'
import { useApp } from '../context/AppContext'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.06 } } }

function WeekCard({ week, index, isExpanded, onToggle }) {
  const completed = week.completed || false
  const hours = week.estimated_hours || 0

  return (
    <motion.div variants={fadeUp} className={`glass-card overflow-hidden transition-all ${completed ? 'ring-2 ring-green-400 dark:ring-green-600' : ''}`}>
      <button onClick={onToggle} className="w-full p-5 flex items-center gap-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${completed ? 'bg-green-100 dark:bg-green-900/30' : 'bg-primary-100 dark:bg-primary-900/30'}`}>
          {completed
            ? <HiOutlineCheckCircle className="w-5 h-5 text-green-600" />
            : <span className="text-primary-600 font-bold text-sm">{week.week_number || index + 1}</span>
          }
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold truncate">{week.title || `Week ${week.week_number || index + 1}`}</h3>
          <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1"><HiOutlineClock className="w-3.5 h-3.5" /> {hours}h</span>
            {week.topics?.length > 0 && <span>{week.topics.length} topics</span>}
            {week.projects?.length > 0 && <span>{week.projects.length} projects</span>}
          </div>
        </div>
        <motion.div animate={{ rotate: isExpanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <HiOutlineChevronDown className="w-5 h-5 text-gray-400" />
        </motion.div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 border-t border-gray-100 dark:border-gray-800 pt-4 space-y-4">
              {week.topics?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Topics</h4>
                  <div className="flex flex-wrap gap-2">
                    {week.topics.map((t, i) => <span key={i} className="badge-blue text-xs">{t}</span>)}
                  </div>
                </div>
              )}
              {week.projects?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Projects</h4>
                  <ul className="space-y-1">
                    {week.projects.map((p, i) => (
                      <li key={i} className="text-sm flex items-center gap-2 text-gray-600 dark:text-gray-400">
                        <HiOutlineRocketLaunch className="w-3.5 h-3.5 text-accent-500 flex-shrink-0" /> {p}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {week.assessments?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Assessments</h4>
                  <ul className="space-y-1">
                    {week.assessments.map((a, i) => (
                      <li key={i} className="text-sm flex items-center gap-2 text-gray-600 dark:text-gray-400">
                        <HiOutlineAcademicCap className="w-3.5 h-3.5 text-green-500 flex-shrink-0" /> {a}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function Roadmap() {
  const { student, roadmap, loading, fetchRoadmap, buildRoadmap } = useApp()
  const [expandedWeeks, setExpandedWeeks] = useState(new Set())
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    if (student?.student_id && !roadmap) fetchRoadmap()
  }, [student, fetchRoadmap, roadmap])

  const weeks = roadmap?.weeks || []
  const completedCount = weeks.filter((w) => w.completed).length
  const progress = weeks.length ? Math.round((completedCount / weeks.length) * 100) : 0

  const toggleWeek = (i) => {
    setExpandedWeeks((prev) => {
      const next = new Set(prev)
      next.has(i) ? next.delete(i) : next.add(i)
      return next
    })
  }

  const handleGenerate = async () => {
    setGenerating(true)
    try { await buildRoadmap() } finally { setGenerating(false) }
  }

  if (loading.roadmap && !roadmap) {
    return <div className="page-container flex items-center justify-center py-32"><LoadingSpinner size="lg" /></div>
  }

  return (
    <div className="page-container max-w-4xl">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        <motion.div variants={fadeUp} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-display font-bold mb-1">Learning Roadmap</h1>
            <p className="text-gray-500 dark:text-gray-400">
              {weeks.length ? `${weeks.length}-week plan • ${completedCount} completed` : 'Generate your personalised roadmap'}
            </p>
          </div>
          <div className="flex gap-2">
            <button onClick={handleGenerate} disabled={generating} className="btn-secondary text-sm flex items-center gap-2">
              {generating ? <HiOutlineArrowPath className="w-4 h-4 animate-spin" /> : <HiOutlineRocketLaunch className="w-4 h-4" />}
              {roadmap ? 'Regenerate' : 'Generate'}
            </button>
          </div>
        </motion.div>

        {/* Progress bar */}
        {weeks.length > 0 && (
          <motion.div variants={fadeUp} className="glass-card p-5 mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Progress</span>
              <span className="text-sm text-gray-500">{completedCount}/{weeks.length} weeks ({progress}%)</span>
            </div>
            <div className="w-full h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <motion.div
                className="h-full gradient-bg rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
              />
            </div>
          </motion.div>
        )}

        {/* Certifications */}
        {roadmap?.certifications?.length > 0 && (
          <motion.div variants={fadeUp} className="glass-card p-5 mb-6">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <HiOutlineAcademicCap className="w-5 h-5 text-accent-500" /> Recommended Certifications
            </h3>
            <div className="flex flex-wrap gap-2">
              {roadmap.certifications.map((c, i) => <span key={i} className="badge-purple">{typeof c === 'string' ? c : c.name || JSON.stringify(c)}</span>)}
            </div>
          </motion.div>
        )}

        {/* Weeks */}
        {weeks.length > 0 ? (
          <motion.div variants={stagger} className="space-y-3">
            {weeks.map((week, i) => (
              <WeekCard
                key={i}
                week={week}
                index={i}
                isExpanded={expandedWeeks.has(i)}
                onToggle={() => toggleWeek(i)}
              />
            ))}
          </motion.div>
        ) : (
          <EmptyState
            icon={HiOutlineMap}
            title="No roadmap yet"
            description="Generate a personalised roadmap based on your profile."
            action={handleGenerate}
            actionLabel="Generate Roadmap"
          />
        )}
      </motion.div>
    </div>
  )
}
