import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  HiOutlineClock,
  HiOutlineArrowTopRightOnSquare,
  HiOutlineAcademicCap,
  HiOutlineBookOpen,
  HiOutlineBriefcase,
  HiOutlineGlobeAlt,
  HiOutlineDocumentText,
  HiOutlinePlus,
  HiOutlineCheckCircle,
  HiOutlineBookmark,
} from 'react-icons/hi2'
import toast from 'react-hot-toast'

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

const typeConfig = {
  course: {
    gradient: 'from-blue-500 to-indigo-600',
    icon: HiOutlineBookOpen,
    label: 'Course',
    primaryAction: { label: 'Open Course', emoji: '\uD83C\uDF93' },
  },
  project: {
    gradient: 'from-purple-500 to-pink-600',
    icon: HiOutlineBriefcase,
    label: 'Project',
  },
  certification: {
    gradient: 'from-emerald-500 to-teal-600',
    icon: HiOutlineAcademicCap,
    label: 'Certification',
    primaryAction: { label: 'View Certification', emoji: '\uD83C\uDFC5' },
  },
  book: {
    gradient: 'from-amber-500 to-orange-600',
    icon: HiOutlineBookmark,
    label: 'Book',
    primaryAction: { label: 'Open Book', emoji: '\uD83D\uDCD8' },
  },
}

function getLevelBadgeClasses(level) {
  const l = String(level || '').toLowerCase()
  if (l.includes('beginner')) return 'bg-white/20 text-white'
  if (l.includes('intermediate')) return 'bg-yellow-300/30 text-yellow-100'
  return 'bg-white/30 text-white'
}

function getDomainIcon(domain) {
  const d = String(domain || '').toLowerCase()
  if (d.includes('web')) return '\uD83C\uDF10'
  if (d.includes('data')) return '\uD83D\uDCCA'
  if (d.includes('machine') || d.includes('ai') || d.includes('artificial')) return '\uD83E\uDD16'
  if (d.includes('cloud')) return '\u2601\uFE0F'
  if (d.includes('devops') || d.includes('linux') || d.includes('git') || d.includes('architecture') || d.includes('automation')) return '\u2699\uFE0F'
  if (d.includes('cyber') || d.includes('security')) return '\uD83D\uDD12'
  if (d.includes('database')) return '\uD83D\uDCBE'
  if (d.includes('ui') || d.includes('ux') || d.includes('design')) return '\uD83C\uDFA8'
  if (d.includes('mobile')) return '\uD83D\uDCF1'
  if (d.includes('blockchain')) return '\uD83D\uDD17'
  if (d.includes('iot') || d.includes('internet of things')) return '\uD83D\uDCBB'
  if (d.includes('nlp') || d.includes('natural language')) return '\uD83D\uDCAC'
  if (d.includes('rag') || d.includes('retrieval')) return '\uD83D\uDCC4'
  if (d.includes('generative') || d.includes('genai')) return '\u2728'
  if (d.includes('trading') || d.includes('finance')) return '\uD83D\uDCC8'
  if (d.includes('network') || d.includes('operating')) return '\uD83C\uDF10'
  return null
}

export default function ResourceCard({ item, type = 'course', showType = false, onViewDetails, onAddToRoadmap }) {
  const config = typeConfig[type] || typeConfig.course
  const Icon = config.icon

  const [added, setAdded] = useState(false)

  const title = item.title || item.name || 'Untitled'
  const skills = item.skills_gained || item.required_skills || item.skills_covered || item.skills || []
  const technologies = item.technologies || []
  const level = item.level || item.difficulty || ''
  const levelStr = typeof level === 'object' ? level.value || level.name || '' : String(level)
  const provider = item.provider || ''
  const domain = item.domain || item.category || ''
  const duration = item.duration || item.estimated_time || ''
  const description = item.description || ''
  const url = item.url || item.exam_link || ''

  const displayTags = [...skills, ...technologies.filter((t) => !skills.includes(t))]

  const handleAddToRoadmap = (e) => {
    e.stopPropagation()
    if (onAddToRoadmap) {
      onAddToRoadmap(item)
    }
    setAdded(true)
    toast.success(`${title} added to roadmap!`)
  }

  const handleViewDetails = (e) => {
    e.stopPropagation()
    if (onViewDetails) onViewDetails(item)
  }

  return (
    <motion.div
      variants={fadeUp}
      whileHover={{ y: -5, transition: { duration: 0.2 } }}
      className="glass-card overflow-hidden flex flex-col group"
    >
      {/* Gradient header */}
      <div className={`bg-gradient-to-r ${config.gradient} px-5 py-4 relative overflow-hidden`}>
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-white/5" />
        <div className="relative flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon className="w-4 h-4 text-white/80" />
            {showType && (
              <span className="text-xs font-semibold text-white/80 uppercase tracking-wider">
                {config.label}
              </span>
            )}
          </div>
          {levelStr && (
            <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${getLevelBadgeClasses(levelStr)}`}>
              {levelStr}
            </span>
          )}
          {item.free && (
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-green-500/90 text-white">
              FREE
            </span>
          )}
        </div>
      </div>

      {/* Card body */}
      <div className="p-5 flex flex-col flex-1">
        <h3 className="font-semibold text-[15px] leading-snug mb-2 line-clamp-2" title={title}>
          {title}
        </h3>

        {/* Meta row */}
        <div className="flex items-center flex-wrap gap-x-3 gap-y-1 text-xs text-gray-500 dark:text-gray-400 mb-3">
          {provider && (
            <span className="flex items-center gap-1">
              <HiOutlineGlobeAlt className="w-3.5 h-3.5 shrink-0" />
              {provider}
            </span>
          )}
          {domain && (
            <span className="flex items-center gap-1">
              <span className="text-[13px] leading-none">{getDomainIcon(domain)}</span>
              {domain}
            </span>
          )}
          {duration && (
            <span className="flex items-center gap-1">
              <HiOutlineClock className="w-3.5 h-3.5 shrink-0" />
              {duration}
            </span>
          )}
        </div>

        {/* Description */}
        {description && (
          <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed line-clamp-3 mb-4">
            {description}
          </p>
        )}

        {/* Skills & Technologies */}
        <div className="mt-auto">
          {displayTags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-4">
              {displayTags.slice(0, 3).map((tag, i) => (
                <span key={i} className="text-[11px] px-2.5 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 font-medium">
                  {tag}
                </span>
              ))}
              {displayTags.length > 3 && (
                <span className="text-[11px] px-2.5 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-400">
                  +{displayTags.length - 3} more
                </span>
              )}
            </div>
          )}

          {/* Actions */}
          {type === 'project' ? (
            <div className="flex gap-2">
              <button
                onClick={handleViewDetails}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 bg-gradient-to-r from-purple-500 to-pink-600 text-white hover:opacity-90 hover:shadow-lg active:scale-[0.97] shadow-sm"
              >
                <HiOutlineDocumentText className="w-4 h-4" />
                View Details
              </button>
              <button
                onClick={handleAddToRoadmap}
                disabled={added}
                className={`flex items-center justify-center gap-1 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  added
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                {added ? <HiOutlineCheckCircle className="w-4 h-4" /> : <HiOutlinePlus className="w-4 h-4" />}
              </button>
            </div>
          ) : url ? (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 bg-gradient-to-r ${config.gradient} text-white hover:opacity-90 hover:shadow-lg active:scale-[0.97] shadow-sm`}
            >
              <span>{config.primaryAction?.emoji}</span>
              {config.primaryAction?.label}
              <HiOutlineArrowTopRightOnSquare className="w-4 h-4 opacity-70" />
            </a>
          ) : (
            <div className="w-full py-2.5 rounded-xl text-sm font-medium text-center text-gray-400 dark:text-gray-600 bg-gray-50 dark:bg-gray-800/50 border border-dashed border-gray-200 dark:border-gray-700">
              No link available
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
