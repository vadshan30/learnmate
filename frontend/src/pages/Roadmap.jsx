import { useEffect, useState, useMemo, useCallback, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  HiOutlineChevronDown, HiOutlineCheckCircle, HiOutlineClock,
  HiOutlineAcademicCap, HiOutlineRocketLaunch, HiOutlineArrowPath,
  HiOutlineTrash, HiOutlineMap, HiOutlineSparkles, HiOutlineBookOpen,
  HiOutlineFlag, HiOutlineTrophy, HiOutlineFire, HiOutlineGlobeAlt,
  HiOutlineMagnifyingGlass, HiOutlineArrowRight, HiOutlineArrowTopRightOnSquare,
  HiOutlineChatBubbleLeftEllipsis, HiOutlineCalendarDays, HiOutlineChartBar,
  HiOutlineFunnel, HiOutlineChevronUp, HiOutlineDocumentText,
  HiOutlineLink, HiOutlineStar, HiOutlineBolt, HiOutlineBriefcase,
} from 'react-icons/hi2'
import { useApp } from '../context/AppContext'
import { deleteRoadmap } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import toast from 'react-hot-toast'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.06 } } }

function CircularProgress({ percentage, size = 80, stroke = 6, color = 'from-primary-500 to-accent-500' }) {
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const offset = c - (percentage / 100) * c
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="currentColor" strokeWidth={stroke}
          className="text-gray-200 dark:text-gray-700" />
        <motion.circle
          cx={size / 2} cy={size / 2} r={r} fill="none" strokeWidth={stroke}
          stroke="url(#progressGradient)" strokeLinecap="round"
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{ strokeDasharray: c }}
        />
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="var(--color-primary-500, #6366f1)" />
            <stop offset="100%" stopColor="var(--color-accent-500, #ec4899)" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-sm font-bold">{Math.round(percentage)}%</span>
      </div>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <motion.div variants={fadeUp} className="glass-card p-4">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <p className="text-xl font-bold leading-tight">{value}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{label}</p>
          {sub && <p className="text-[11px] text-gray-400 dark:text-gray-500">{sub}</p>}
        </div>
      </div>
    </motion.div>
  )
}

function StatusBadge({ status }) {
  const s = String(status || '').toLowerCase()
  if (s === 'completed') return <span className="badge-green text-[11px]">Completed</span>
  if (s === 'in_progress') return <span className="badge-yellow text-[11px]">In Progress</span>
  return <span className="badge-blue text-[11px]">Not Started</span>
}

function DifficultyBadge({ level }) {
  const l = String(level || '').toLowerCase()
  if (l.includes('beginner')) return <span className="badge-green text-[10px]">Beginner</span>
  if (l.includes('intermediate')) return <span className="badge-yellow text-[10px]">Intermediate</span>
  if (l.includes('advanced')) return <span className="badge-red text-[10px]">Advanced</span>
  return null
}

function WeekTimelineCard({ week, index, isExpanded, onToggle, onToggleTopic, completedTopics, isLast }) {
  const isCompleted = week.completed || week.completion_status === 'completed'
  const isInProgress = week.completion_status === 'in_progress'
  const hours = week.estimated_hours || 0
  const topics = week.topics || []
  const projects = week.projects || []
  const assessments = week.assessments || []
  const completedCount = topics.filter((t) => completedTopics.has(t.toLowerCase().trim())).length
  const weekPercent = topics.length > 0 ? Math.round((completedCount / topics.length) * 100) : (isCompleted ? 100 : 0)

  return (
    <motion.div variants={fadeUp} className="relative flex gap-4 sm:gap-6">
      {/* Timeline line + dot */}
      <div className="flex flex-col items-center flex-shrink-0">
        <motion.button
          onClick={onToggle}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          className={`relative z-10 w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center flex-shrink-0 border-4 transition-colors ${
            isCompleted
              ? 'bg-green-500 border-green-200 dark:border-green-900 text-white'
              : isInProgress
                ? 'bg-yellow-500 border-yellow-200 dark:border-yellow-900 text-white'
                : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400'
          }`}
        >
          {isCompleted ? (
            <HiOutlineCheckCircle className="w-5 h-5 sm:w-6 sm:h-6" />
          ) : (
            <span className="text-sm font-bold">{week.week_number || index + 1}</span>
          )}
        </motion.button>
        {!isLast && (
          <div className={`w-0.5 flex-1 min-h-[20px] ${isCompleted ? 'bg-green-300 dark:bg-green-700' : 'bg-gray-200 dark:bg-gray-700'}`} />
        )}
      </div>

      {/* Card */}
      <div className={`flex-1 pb-6 min-w-0`}>
        <motion.div
          className={`glass-card overflow-hidden transition-all ${
            isCompleted ? 'ring-2 ring-green-400/50 dark:ring-green-600/50' : isInProgress ? 'ring-1 ring-yellow-400/50 dark:ring-yellow-600/50' : ''
          }`}
          whileHover={{ y: -1 }}
        >
          {/* Header */}
          <button onClick={onToggle} className="w-full p-4 sm:p-5 flex items-center gap-3 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Week {week.week_number || index + 1}</span>
                <StatusBadge status={week.completion_status || (isCompleted ? 'completed' : 'not_started')} />
              </div>
              <h3 className="font-semibold text-[15px] truncate">{week.title || `Week ${week.week_number || index + 1}`}</h3>
              <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 mt-1.5">
                <span className="flex items-center gap-1"><HiOutlineClock className="w-3.5 h-3.5" /> {hours}h</span>
                {topics.length > 0 && <span>{completedCount}/{topics.length} topics</span>}
                {projects.length > 0 && <span>{projects.length} project{projects.length > 1 ? 's' : ''}</span>}
                {assessments.length > 0 && <span>{assessments.length} cert{assessments.length > 1 ? 's' : ''}</span>}
              </div>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              {weekPercent > 0 && !isCompleted && (
                <div className="hidden sm:block w-16">
                  <div className="text-[10px] text-center font-semibold text-primary-600 dark:text-primary-400 mb-0.5">{weekPercent}%</div>
                  <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full" style={{ width: `${weekPercent}%` }} />
                  </div>
                </div>
              )}
              <motion.div animate={{ rotate: isExpanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
                <HiOutlineChevronDown className="w-5 h-5 text-gray-400" />
              </motion.div>
            </div>
          </button>

          {/* Expanded content */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25 }}
                className="overflow-hidden"
              >
                <div className="px-4 sm:px-5 pb-5 border-t border-gray-100 dark:border-gray-800 pt-4 space-y-4">
                  {/* Objectives / Topics */}
                  {topics.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <HiOutlineCheckCircle className="w-3.5 h-3.5" /> Objectives
                      </h4>
                      <div className="space-y-1.5">
                        {topics.map((t, i) => {
                          const isDone = completedTopics.has(t.toLowerCase().trim())
                          return (
                            <button
                              key={i}
                              onClick={(e) => { e.stopPropagation(); onToggleTopic(t, !isDone) }}
                              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-left transition-all ${
                                isDone
                                  ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400'
                                  : 'bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                              }`}
                            >
                              <div className={`w-5 h-5 rounded flex items-center justify-center border-2 shrink-0 transition-colors ${
                                isDone ? 'bg-green-500 border-green-500' : 'border-gray-300 dark:border-gray-600'
                              }`}>
                                {isDone && (
                                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                  </svg>
                                )}
                              </div>
                              <span className={isDone ? 'line-through opacity-70' : ''}>{t}</span>
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  )}

                  {/* Projects */}
                  {projects.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <HiOutlineRocketLaunch className="w-3.5 h-3.5 text-accent-500" /> Projects
                      </h4>
                      <div className="space-y-2">
                        {projects.map((p, i) => (
                          <div key={i} className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg bg-gradient-to-r from-accent-50 to-primary-50 dark:from-accent-900/10 dark:to-primary-900/10 border border-accent-100 dark:border-accent-900/20">
                            <HiOutlineRocketLaunch className="w-4 h-4 text-accent-500 shrink-0" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{p}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Certifications */}
                  {assessments.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <HiOutlineAcademicCap className="w-3.5 h-3.5 text-green-500" /> Certifications
                      </h4>
                      <div className="space-y-2">
                        {assessments.map((a, i) => (
                          <div key={i} className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/20">
                            <HiOutlineAcademicCap className="w-4 h-4 text-green-500 shrink-0" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{a}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Week progress bar */}
                  {topics.length > 0 && (
                    <div className="pt-2">
                      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-1.5">
                        <span>Week Progress</span>
                        <span className="font-semibold">{completedCount}/{topics.length} ({weekPercent}%)</span>
                      </div>
                      <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${weekPercent}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </motion.div>
  )
}

function CertificationCard({ cert }) {
  const name = typeof cert === 'string' ? cert : cert.name || cert.title || 'Certification'
  const provider = typeof cert === 'object' ? (cert.provider || cert.issuer || '') : ''
  const difficulty = typeof cert === 'object' ? (cert.difficulty || cert.level || '') : ''
  const url = typeof cert === 'object' ? (cert.url || cert.link || cert.exam_link || '') : ''
  const duration = typeof cert === 'object' ? (cert.duration || '') : ''

  return (
    <motion.div variants={fadeUp} whileHover={{ y: -2 }} className="glass-card p-4 overflow-hidden">
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 px-4 py-3 -mx-0 -mt-0 mb-3">
        <div className="flex items-center gap-2">
          <HiOutlineAcademicCap className="w-5 h-5 text-white/80" />
          <span className="text-xs font-semibold text-white/80 uppercase tracking-wider">Certification</span>
        </div>
      </div>
      <h4 className="font-semibold text-sm mb-1 line-clamp-2">{name}</h4>
      <div className="flex items-center gap-2 flex-wrap text-xs text-gray-500 dark:text-gray-400 mb-2">
        {provider && <span>{provider}</span>}
        {duration && <><span>&middot;</span><span>{duration}</span></>}
      </div>
      {difficulty && <DifficultyBadge level={difficulty} />}
      {url && (
        <a href={url} target="_blank" rel="noopener noreferrer"
          className="mt-3 w-full flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors">
          View Certification <HiOutlineArrowTopRightOnSquare className="w-3 h-3" />
        </a>
      )}
    </motion.div>
  )
}

function ProjectCard({ name }) {
  return (
    <motion.div variants={fadeUp} whileHover={{ y: -2 }} className="glass-card p-4">
      <div className="bg-gradient-to-r from-accent-500 to-pink-600 px-4 py-3 -mx-0 -mt-0 mb-3">
        <div className="flex items-center gap-2">
          <HiOutlineRocketLaunch className="w-5 h-5 text-white/80" />
          <span className="text-xs font-semibold text-white/80 uppercase tracking-wider">Project</span>
        </div>
      </div>
      <h4 className="font-semibold text-sm mb-2">{name}</h4>
      <Link to="/resources"
        className="w-full flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium bg-accent-50 dark:bg-accent-900/20 text-accent-700 dark:text-accent-400 hover:bg-accent-100 dark:hover:bg-accent-900/30 transition-colors">
        View Resources <HiOutlineArrowTopRightOnSquare className="w-3 h-3" />
      </Link>
    </motion.div>
  )
}

function MilestoneCard({ icon: Icon, title, description, achieved, color }) {
  return (
    <motion.div
      variants={fadeUp}
      className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
        achieved
          ? 'bg-gradient-to-r from-primary-50 to-accent-50 dark:from-primary-900/10 dark:to-accent-900/10 border-primary-200 dark:border-primary-800'
          : 'bg-gray-50 dark:bg-gray-800/30 border-gray-200 dark:border-gray-700 opacity-60'
      }`}
    >
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${achieved ? color : 'bg-gray-200 dark:bg-gray-700 text-gray-400'}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="min-w-0">
        <p className="text-sm font-semibold">{title}</p>
        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{description}</p>
      </div>
      {achieved && <HiOutlineCheckCircle className="w-5 h-5 text-green-500 shrink-0 ml-auto" />}
    </motion.div>
  )
}

export default function Roadmap() {
  const { student, roadmap, loading, fetchRoadmap, buildRoadmap, completeTopic, fetchProgress } = useApp()
  const navigate = useNavigate()
  const [expandedWeeks, setExpandedWeeks] = useState(new Set())
  const [generating, setGenerating] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const timelineRef = useRef(null)

  useEffect(() => {
    if (student?.student_id && !roadmap) fetchRoadmap()
  }, [student, fetchRoadmap, roadmap])

  const weeks = roadmap?.weeks || []
  const totalWeeks = weeks.length
  const completedCount = weeks.filter((w) => w.completed || w.completion_status === 'completed').length
  const progress = roadmap?.progress?.percentage ?? (totalWeeks ? Math.round((completedCount / totalWeeks) * 100) : 0)
  const completedTopicsList = roadmap?.completed_topics || []
  const completedTopicsSet = new Set(completedTopicsList.map((t) => t.toLowerCase().trim()))
  const totalTopics = roadmap?.total_topics || weeks.reduce((sum, w) => sum + (w.topics?.length || 0), 0)
  const totalHours = weeks.reduce((sum, w) => sum + (w.estimated_hours || 0), 0)
  const completedHours = weeks.filter((w) => w.completed || w.completion_status === 'completed').reduce((sum, w) => sum + (w.estimated_hours || 0), 0)
  const allTopics = weeks.flatMap((w) => w.topics || [])
  const completedTopicCount = allTopics.filter((t) => completedTopicsSet.has(t.toLowerCase().trim())).length
  const allProjects = [...new Set(weeks.flatMap((w) => w.projects || []))]
  const allCerts = [...new Map((roadmap?.certifications || []).map((c) => [c.id || c.name || c, c])).values()]
  const uniqueSkills = [...new Set([...(student?.current_skills || []), ...allTopics.slice(0, 12)])]

  const filteredWeeks = useMemo(() => {
    let list = weeks
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      list = list.filter((w) =>
        (w.title || '').toLowerCase().includes(q) ||
        (w.topics || []).some((t) => t.toLowerCase().includes(q)) ||
        (w.projects || []).some((p) => p.toLowerCase().includes(q))
      )
    }
    if (filterStatus === 'completed') list = list.filter((w) => w.completed || w.completion_status === 'completed')
    else if (filterStatus === 'pending') list = list.filter((w) => !w.completed && w.completion_status !== 'completed')
    else if (filterStatus === 'projects') list = list.filter((w) => w.projects?.length > 0)
    else if (filterStatus === 'certs') list = list.filter((w) => w.assessments?.length > 0)
    return list
  }, [weeks, searchQuery, filterStatus])

  const toggleWeek = (i) => {
    setExpandedWeeks((prev) => {
      const next = new Set(prev)
      next.has(i) ? next.delete(i) : next.add(i)
      return next
    })
  }

  const expandAll = () => setExpandedWeeks(new Set(weeks.map((_, i) => i)))
  const collapseAll = () => setExpandedWeeks(new Set())

  const handleToggleTopic = async (topicName, completed) => {
    try {
      await completeTopic(topicName, completed)
      toast.success(completed ? `Completed "${topicName}"` : `Uncompleted "${topicName}"`)
    } catch {
      toast.error('Failed to update topic')
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    try { await buildRoadmap() } finally { setGenerating(false) }
  }

  const handleDelete = async () => {
    if (!confirm('Delete your roadmap? This cannot be undone.')) return
    try {
      await deleteRoadmap(student.student_id)
      window.location.reload()
    } catch {
      toast.error('Failed to delete roadmap')
    }
  }

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(roadmap, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `roadmap-${student?.name || 'export'}.json`; a.click()
    URL.revokeObjectURL(url)
    toast.success('Roadmap exported')
  }

  const handleExportPDF = () => { window.print() }

  const currentWeek = weeks.find((w) => !w.completed && w.completion_status !== 'completed')
  const weakestSkill = (() => {
    const skills = student?.current_skills || []
    if (skills.length === 0) return 'Programming'
    const completedLower = new Set(
      (roadmap?.completed_topics || []).map((t) => t.toLowerCase())
    )
    // Find the skill that appears least in completed topics
    let weakest = skills[0]
    let minMentions = Infinity
    for (const skill of skills) {
      const mentions = [...completedLower].filter((t) =>
        t.includes(skill.toLowerCase())
      ).length
      if (mentions < minMentions) {
        minMentions = mentions
        weakest = skill
      }
    }
    return weakest
  })()

  // Milestones
  const milestones = [
    { icon: HiOutlineFlag, title: 'First Step', description: 'Start your first week', achieved: completedCount >= 1 || completedTopicCount >= 1, color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600' },
    { icon: HiOutlineCheckCircle, title: 'Week 1 Done', description: 'Complete your first week', achieved: completedCount >= 1, color: 'bg-green-100 dark:bg-green-900/30 text-green-600' },
    { icon: HiOutlineBolt, title: 'Momentum', description: 'Complete 3 weeks', achieved: completedCount >= 3, color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600' },
    { icon: HiOutlineFire, title: 'Halfway There', description: 'Complete 50% of weeks', achieved: completedCount >= Math.ceil(totalWeeks / 2), color: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600' },
    { icon: HiOutlineTrophy, title: 'Achiever', description: 'Complete 75% of weeks', achieved: completedCount >= Math.ceil(totalWeeks * 0.75), color: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600' },
    { icon: HiOutlineStar, title: 'Roadmap Master', description: 'Complete all weeks', achieved: completedCount >= totalWeeks && totalWeeks > 0, color: 'bg-gradient-to-r from-primary-500 to-accent-500 text-white' },
  ]

  const milestonesAchieved = milestones.filter((m) => m.achieved).length

  if (loading.roadmap && !roadmap) {
    return <div className="page-container flex items-center justify-center py-32"><LoadingSpinner size="lg" /></div>
  }

  return (
    <div className="page-container max-w-[1400px]">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        {/* ─── Header ──────────────────────────────────── */}
        <motion.div variants={fadeUp} className="glass-card p-6 sm:p-8 mb-6 overflow-hidden">
          <div className="bg-gradient-to-r from-primary-600 via-primary-500 to-accent-500 -mx-6 sm:-mx-8 -mt-6 sm:-mt-8 px-6 sm:px-8 py-6 sm:py-8 mb-6">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <HiOutlineMap className="w-5 h-5 text-white/80" />
                  <span className="text-xs font-semibold text-white/80 uppercase tracking-wider">Personalized Learning Roadmap</span>
                </div>
                <h1 className="text-2xl sm:text-3xl font-display font-bold text-white mb-3">
                  {student?.name ? `${student.name}'s Roadmap` : 'Learning Roadmap'}
                </h1>
                <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-white/80">
                  {student?.career_goal && <span className="flex items-center gap-1.5"><HiOutlineBriefcase className="w-4 h-4" /> {student.career_goal}</span>}
                  {student?.skill_level && <span className="flex items-center gap-1.5"><HiOutlineChartBar className="w-4 h-4" /> {student.skill_level}</span>}
                  {totalWeeks > 0 && <span className="flex items-center gap-1.5"><HiOutlineCalendarDays className="w-4 h-4" /> {totalWeeks} Weeks</span>}
                  {totalHours > 0 && <span className="flex items-center gap-1.5"><HiOutlineClock className="w-4 h-4" /> {totalHours} Hours</span>}
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <button onClick={handleGenerate} disabled={generating}
                  className="px-4 py-2.5 rounded-xl text-sm font-semibold bg-white/20 text-white hover:bg-white/30 transition-colors flex items-center gap-2">
                  {generating ? <HiOutlineArrowPath className="w-4 h-4 animate-spin" /> : <HiOutlineRocketLaunch className="w-4 h-4" />}
                  {roadmap ? 'Regenerate' : 'Generate'}
                </button>
                {roadmap && (
                  <>
                    <button onClick={handleExportPDF}
                      className="px-4 py-2.5 rounded-xl text-sm font-medium bg-white/10 text-white/90 hover:bg-white/20 transition-colors flex items-center gap-2">
                      <HiOutlineDocumentText className="w-4 h-4" /> PDF
                    </button>
                    <button onClick={handleExportJSON}
                      className="px-4 py-2.5 rounded-xl text-sm font-medium bg-white/10 text-white/90 hover:bg-white/20 transition-colors flex items-center gap-2">
                      <HiOutlineArrowTopRightOnSquare className="w-4 h-4" /> JSON
                    </button>
                    <Link to="/chat"
                      className="px-4 py-2.5 rounded-xl text-sm font-medium bg-white/10 text-white/90 hover:bg-white/20 transition-colors flex items-center gap-2">
                      <HiOutlineChatBubbleLeftEllipsis className="w-4 h-4" /> AI Mentor
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Analytics cards */}
          {weeks.length > 0 && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              <StatCard icon={HiOutlineChartBar} label="Overall Progress" value={`${Math.round(progress)}%`} sub={`${completedTopicCount}/${totalTopics} topics`} color="bg-primary-100 dark:bg-primary-900/30 text-primary-600" />
              <StatCard icon={HiOutlineCheckCircle} label="Completed Weeks" value={`${completedCount} / ${totalWeeks}`} sub={completedCount === totalWeeks ? 'All done!' : `${totalWeeks - completedCount} remaining`} color="bg-green-100 dark:bg-green-900/30 text-green-600" />
              <StatCard icon={HiOutlineClock} label="Study Hours" value={`${completedHours} / ${totalHours}`} sub={`${totalHours - completedHours}h remaining`} color="bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600" />
              <StatCard icon={HiOutlineFire} label="Current Streak" value={`${completedCount} Week${completedCount !== 1 ? 's' : ''}`} sub={`${milestonesAchieved}/${milestones.length} milestones`} color="bg-orange-100 dark:bg-orange-900/30 text-orange-600" />
            </div>
          )}
        </motion.div>

        {weeks.length === 0 ? (
          <EmptyState
            icon={HiOutlineMap}
            title="No roadmap yet"
            description="Generate a personalised roadmap based on your profile."
            action={handleGenerate}
            actionLabel="Generate Roadmap"
          />
        ) : (
          <div className="flex flex-col lg:flex-row gap-6">
            {/* ─── Main Content ──────────────────────────── */}
            <div className="flex-1 min-w-0 space-y-6">
              {/* Skill chips */}
              {uniqueSkills.length > 0 && (
                <motion.div variants={fadeUp} className="glass-card p-5">
                  <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <HiOutlineSparkles className="w-4 h-4 text-primary-500" /> Skill Roadmap
                  </h2>
                  <div className="flex flex-wrap gap-2">
                    {uniqueSkills.map((skill, i) => (
                      <motion.span key={skill} variants={fadeUp}
                        className="px-3 py-1.5 rounded-lg text-sm font-medium bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 border border-primary-100 dark:border-primary-800/30">
                        {skill}
                      </motion.span>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Search + Filter bar */}
              <motion.div variants={fadeUp} className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <HiOutlineMagnifyingGlass className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search weeks, topics, projects..."
                    className="input-field !pl-10 !py-2.5 text-sm"
                  />
                </div>
                <div className="flex gap-2 flex-wrap">
                  {[
                    { key: 'all', label: 'All' },
                    { key: 'completed', label: 'Completed' },
                    { key: 'pending', label: 'Pending' },
                    { key: 'projects', label: 'Projects' },
                    { key: 'certs', label: 'Certs' },
                  ].map((f) => (
                    <button key={f.key} onClick={() => setFilterStatus(f.key)}
                      className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                        filterStatus === f.key
                          ? 'bg-primary-500 text-white shadow-sm'
                          : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                      }`}>
                      {f.label}
                    </button>
                  ))}
                  <button onClick={expandAll} className="px-3 py-2 rounded-lg text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center gap-1">
                    <HiOutlineChevronDown className="w-3 h-3" /> All
                  </button>
                  <button onClick={collapseAll} className="px-3 py-2 rounded-lg text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center gap-1">
                    <HiOutlineChevronUp className="w-3 h-3" /> All
                  </button>
                </div>
              </motion.div>

              {/* Timeline */}
              <motion.div ref={timelineRef} variants={stagger} className="space-y-0">
                {filteredWeeks.length > 0 ? (
                  filteredWeeks.map((week, i) => {
                    const realIndex = weeks.indexOf(week)
                    return (
                      <WeekTimelineCard
                        key={realIndex}
                        week={week}
                        index={realIndex}
                        isExpanded={expandedWeeks.has(realIndex)}
                        onToggle={() => toggleWeek(realIndex)}
                        onToggleTopic={handleToggleTopic}
                        completedTopics={completedTopicsSet}
                        isLast={realIndex === filteredWeeks.length - 1}
                      />
                    )
                  })
                ) : (
                  <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                    <HiOutlineMagnifyingGlass className="w-8 h-8 mx-auto mb-3 opacity-50" />
                    <p className="text-sm">No weeks match your search or filter.</p>
                  </div>
                )}
              </motion.div>

              {/* Projects showcase */}
              {allProjects.length > 0 && (
                <motion.div variants={fadeUp}>
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <HiOutlineRocketLaunch className="w-5 h-5 text-accent-500" /> Projects
                  </h2>
                  <motion.div variants={stagger} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {allProjects.map((p, i) => <ProjectCard key={i} name={p} />)}
                  </motion.div>
                </motion.div>
              )}

              {/* Certifications */}
              {allCerts.length > 0 && (
                <motion.div variants={fadeUp}>
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <HiOutlineAcademicCap className="w-5 h-5 text-green-500" /> Certifications
                  </h2>
                  <motion.div variants={stagger} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {allCerts.map((c, i) => <CertificationCard key={i} cert={c} />)}
                  </motion.div>
                </motion.div>
              )}

              {/* Milestones */}
              <motion.div variants={fadeUp}>
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <HiOutlineTrophy className="w-5 h-5 text-yellow-500" /> Milestones
                  <span className="text-xs font-normal text-gray-400 ml-1">{milestonesAchieved}/{milestones.length} achieved</span>
                </h2>
                <motion.div variants={stagger} className="grid sm:grid-cols-2 gap-2.5">
                  {milestones.map((m, i) => <MilestoneCard key={i} {...m} />)}
                </motion.div>
              </motion.div>
            </div>

            {/* ─── Right Sidebar ──────────────────────────── */}
            <div className="w-full lg:w-80 shrink-0 space-y-4 lg:sticky lg:top-24 lg:self-start">
              {/* Overall circular progress */}
              <motion.div variants={fadeUp} className="glass-card p-5 text-center">
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">Overall Progress</h3>
                <div className="flex justify-center mb-4">
                  <CircularProgress percentage={progress} size={100} stroke={8} />
                </div>
                <div className="grid grid-cols-2 gap-3 text-center">
                  <div>
                    <p className="text-lg font-bold">{completedCount}/{totalWeeks}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Weeks</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold">{completedTopicCount}/{totalTopics}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Topics</p>
                  </div>
                </div>
              </motion.div>

              {/* Upcoming week */}
              {currentWeek && (
                <motion.div variants={fadeUp} className="glass-card p-5">
                  <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                    <HiOutlineBolt className="w-4 h-4 text-yellow-500" /> Upcoming
                  </h3>
                  <div className="p-3 rounded-xl bg-primary-50 dark:bg-primary-900/20 border border-primary-100 dark:border-primary-800/30">
                    <p className="text-xs font-semibold text-primary-600 dark:text-primary-400 mb-1">Week {currentWeek.week_number}</p>
                    <p className="text-sm font-medium line-clamp-2">{currentWeek.title}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{currentWeek.estimated_hours || 0}h &middot; {(currentWeek.topics || []).length} topics</p>
                  </div>
                </motion.div>
              )}

              {/* AI Recommendations */}
              <motion.div variants={fadeUp} className="glass-card p-5">
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <HiOutlineSparkles className="w-4 h-4 text-accent-500" /> AI Recommendations
                </h3>
                <div className="space-y-3">
                  <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-0.5">Next Topic</p>
                    <p className="text-sm font-medium">{currentWeek?.topics?.[0] || 'Continue your current week'}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-0.5">Weakest Skill</p>
                    <p className="text-sm font-medium">{weakestSkill}</p>
                  </div>
                  {allProjects[0] && (
                    <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                      <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-0.5">Suggested Project</p>
                      <p className="text-sm font-medium">{allProjects[0]}</p>
                    </div>
                  )}
                </div>
              </motion.div>

              {/* Quick nav */}
              <motion.div variants={fadeUp} className="glass-card p-5">
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Quick Navigation</h3>
                <div className="space-y-1.5 max-h-48 overflow-y-auto">
                  {weeks.map((w, i) => {
                    const isDone = w.completed || w.completion_status === 'completed'
                    return (
                      <button key={i} onClick={() => {
                        setExpandedWeeks((prev) => new Set([...prev, i]))
                        setTimeout(() => {
                          const el = timelineRef.current?.children?.[weeks.indexOf(w)]
                          el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
                        }, 100)
                      }}
                        className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs text-left transition-colors ${
                          isDone ? 'text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/10' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
                        }`}>
                        {isDone ? <HiOutlineCheckCircle className="w-3.5 h-3.5 shrink-0" /> : <div className="w-3.5 h-3.5 rounded border border-gray-300 dark:border-gray-600 shrink-0" />}
                        <span className="truncate">W{w.week_number || i + 1}: {w.title || 'Untitled'}</span>
                      </button>
                    )
                  })}
                </div>
              </motion.div>

              {/* Study reminder */}
              <motion.div variants={fadeUp} className="glass-card p-5">
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <HiOutlineClock className="w-4 h-4 text-primary-500" /> Study Reminder
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {totalHours - completedHours > 0
                    ? `You have ${totalHours - completedHours} hours of study remaining. Keep going!`
                    : 'Congratulations! You have completed all estimated study hours.'}
                </p>
              </motion.div>

              {/* Roadmap summary stats */}
              <motion.div variants={fadeUp} className="glass-card p-5">
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Summary</h3>
                <div className="space-y-2.5">
                  {[
                    { label: 'Total Courses', value: totalTopics, icon: HiOutlineBookOpen },
                    { label: 'Total Projects', value: allProjects.length, icon: HiOutlineRocketLaunch },
                    { label: 'Certifications', value: allCerts.length, icon: HiOutlineAcademicCap },
                    { label: 'Topics Completed', value: completedTopicCount, icon: HiOutlineCheckCircle },
                    { label: 'Hours Remaining', value: `${totalHours - completedHours}h`, icon: HiOutlineClock },
                    { label: 'Weeks Remaining', value: totalWeeks - completedCount, icon: HiOutlineCalendarDays },
                  ].map((s, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                        <s.icon className="w-4 h-4 text-gray-400" /> {s.label}
                      </span>
                      <span className="font-semibold">{s.value}</span>
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* Danger zone */}
              <motion.div variants={fadeUp} className="glass-card p-5">
                <button onClick={handleDelete}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/10 hover:bg-red-100 dark:hover:bg-red-900/20 transition-colors">
                  <HiOutlineTrash className="w-4 h-4" /> Delete Roadmap
                </button>
              </motion.div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
