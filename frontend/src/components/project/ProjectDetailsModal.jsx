import { useEffect, useState, useCallback, useRef, memo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Component } from 'react'
import {
  HiOutlineXMark,
  HiOutlineClock,
  HiOutlineCheckCircle,
  HiOutlineArrowTopRightOnSquare,
  HiOutlineBookOpen,
  HiOutlineWrench,
  HiOutlineLightBulb,
  HiOutlineGlobeAlt,
  HiOutlineStar,
  HiOutlineAcademicCap,
  HiOutlineRocketLaunch,
  HiOutlineShieldCheck,
  HiOutlineSparkles,
  HiOutlineExclamationTriangle,
  HiOutlineArrowPath,
  HiOutlinePlus,
  HiOutlineTag,
} from 'react-icons/hi2'
import { useApp } from '../../context/AppContext'
import { getProjectDetails, getProjectResources, getRecommendedCourses, saveProject, completeProject } from '../../services/api'
import toast from 'react-hot-toast'

const overlay = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
}

const modalAnim = {
  hidden: { opacity: 0, scale: 0.95, y: 20 },
  visible: { opacity: 1, scale: 1, y: 0, transition: { type: 'spring', damping: 25, stiffness: 300 } },
  exit: { opacity: 0, scale: 0.95, y: 20, transition: { duration: 0.15 } },
}

const DIFFICULTY_COLORS = {
  beginner: 'bg-emerald-500/20 text-emerald-100 border border-emerald-400/30',
  intermediate: 'bg-yellow-500/20 text-yellow-100 border border-yellow-400/30',
  advanced: 'bg-red-500/20 text-red-100 border border-red-400/30',
}

function getDifficultyBadgeClasses(level) {
  const l = String(level || '').toLowerCase()
  if (l.includes('beginner')) return DIFFICULTY_COLORS.beginner
  if (l.includes('intermediate')) return DIFFICULTY_COLORS.intermediate
  if (l.includes('advanced')) return DIFFICULTY_COLORS.advanced
  return 'bg-white/20 text-white'
}

function getTechColor(tech) {
  const t = String(tech || '').toLowerCase()
  if (t.includes('python')) return 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300'
  if (t.includes('react') || t.includes('javascript')) return 'bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-300'
  if (t.includes('docker') || t.includes('kubernetes')) return 'bg-sky-100 dark:bg-sky-900/40 text-sky-700 dark:text-sky-300'
  if (t.includes('aws') || t.includes('lambda') || t.includes('cloud')) return 'bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300'
  if (t.includes('tensorflow') || t.includes('keras') || t.includes('scikit')) return 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300'
  if (t.includes('fastapi') || t.includes('flask') || t.includes('django')) return 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300'
  if (t.includes('sql') || t.includes('postgres') || t.includes('mongo') || t.includes('dynamo')) return 'bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300'
  if (t.includes('git') || t.includes('github')) return 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
  if (t.includes('nlp') || t.includes('transformer') || t.includes('hugging')) return 'bg-fuchsia-100 dark:bg-fuchsia-900/40 text-fuchsia-700 dark:text-fuchsia-300'
  if (t.includes('nmap') || t.includes('scapy') || t.includes('wireshark')) return 'bg-rose-100 dark:bg-rose-900/40 text-rose-700 dark:text-rose-300'
  return 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300'
}

function Section({ icon: Icon, title, children, count }) {
  if (!children) return null
  return (
    <div className="mb-6">
      <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        <Icon className="w-4 h-4 text-primary-500" />
        {title}
        {typeof count === 'number' && (
          <span className="text-[11px] px-1.5 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 font-medium">
            {count}
          </span>
        )}
      </h4>
      {children}
    </div>
  )
}

function ResourceLink({ item }) {
  if (!item?.url) return null
  return (
    <a
      href={item.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group text-sm border border-gray-100 dark:border-gray-800"
    >
      <HiOutlineGlobeAlt className="w-4 h-4 text-gray-400 shrink-0" />
      <span className="text-gray-700 dark:text-gray-300 truncate flex-1">{item.name || 'Resource'}</span>
      <HiOutlineArrowTopRightOnSquare className="w-3.5 h-3.5 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
    </a>
  )
}

function CourseCard({ course }) {
  const matchScore = Math.round((course?._match_score || 0) * 100)
  const matchedSkills = course?._matched_skills || []
  return (
    <div className="flex items-start gap-3 p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800 hover:border-gray-200 dark:hover:border-gray-700 transition-colors">
      <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center shrink-0 shadow-sm">
        <HiOutlineBookOpen className="w-5 h-5 text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <h5 className="font-medium text-sm line-clamp-1">{course?.title || 'Course'}</h5>
        <div className="flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400">
          {course?.provider && <span>{course.provider}</span>}
          {course?.provider && course?.duration && <span>&middot;</span>}
          {course?.duration && <span>{course.duration}</span>}
          {course?.level && (
            <>
              <span>&middot;</span>
              <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                String(course.level).toLowerCase().includes('beginner')
                  ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400'
                  : String(course.level).toLowerCase().includes('intermediate')
                    ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                    : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
              }`}>
                {course.level}
              </span>
            </>
          )}
        </div>
        {matchedSkills.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {matchedSkills.slice(0, 4).map((s, i) => (
              <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 font-medium">
                {s}
              </span>
            ))}
            {matchedSkills.length > 4 && (
              <span className="text-[10px] px-1.5 py-0.5 rounded text-gray-400">+{matchedSkills.length - 4}</span>
            )}
          </div>
        )}
        {matchScore > 0 && (
          <div className="flex items-center gap-2 mt-2">
            <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full transition-all duration-500"
                style={{ width: `${matchScore}%` }}
              />
            </div>
            <span className="text-[10px] font-semibold text-primary-600 dark:text-primary-400">{matchScore}% match</span>
          </div>
        )}
      </div>
      {course?.url && (
        <a
          href={course.url}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 hover:bg-primary-100 dark:hover:bg-primary-900/50 transition-colors flex items-center gap-1"
        >
          Start
          <HiOutlineArrowTopRightOnSquare className="w-3 h-3" />
        </a>
      )}
    </div>
  )
}

class ModalErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={this.props.onClose}>
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
          <div
            className="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-8 max-w-sm w-full text-center space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <HiOutlineExclamationTriangle className="w-12 h-12 text-yellow-500 mx-auto" />
            <h2 className="text-xl font-display font-bold">Something went wrong</h2>
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              {this.state.error?.message || 'Failed to load project details.'}
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => { this.setState({ hasError: false, error: null }) }}
                className="btn-secondary flex items-center gap-2 text-sm"
              >
                <HiOutlineArrowPath className="w-4 h-4" />
                Retry
              </button>
              <button onClick={this.props.onClose} className="btn-primary text-sm">
                Close
              </button>
            </div>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

const ProjectDetailsModal = memo(function ProjectDetailsModal({ project, isOpen, onClose }) {
  const { student } = useApp()
  const [resources, setResources] = useState(null)
  const [details, setDetails] = useState(null)
  const [recommendedCourses, setRecommendedCourses] = useState([])
  const [saving, setSaving] = useState(false)
  const [completing, setCompleting] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)
  const [addedToRoadmap, setAddedToRoadmap] = useState(false)
  const previousFocusRef = useRef(null)
  const modalContentRef = useRef(null)

  const projectId = project?.id

  useEffect(() => {
    if (!isOpen || !projectId) return
    previousFocusRef.current = document.activeElement
    setDetails(null)
    setResources(null)
    setRecommendedCourses([])
    setIsSaved(false)
    setIsCompleted(false)
    setAddedToRoadmap(false)

    getProjectDetails(projectId).then((r) => {
      setDetails(r.data?.data || project)
    }).catch(() => {
      setDetails(project)
    })

    getProjectResources(projectId).then((r) => {
      setResources(r.data?.data || null)
    }).catch(() => {
      setResources(null)
    })

    getRecommendedCourses(projectId, { student_id: student?.student_id }).then((r) => {
      setRecommendedCourses(r.data?.data?.courses || [])
    }).catch(() => {
      setRecommendedCourses([])
    })
  }, [isOpen, projectId, project, student?.student_id])

  useEffect(() => {
    if (!isOpen) return
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleEsc)
    return () => document.removeEventListener('keydown', handleEsc)
  }, [isOpen, onClose])

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  useEffect(() => {
    if (!isOpen && previousFocusRef.current && previousFocusRef.current.focus) {
      previousFocusRef.current.focus()
      previousFocusRef.current = null
    }
  }, [isOpen])

  const handleSave = useCallback(async () => {
    if (!student?.student_id) { toast.error('Create a profile first'); return }
    if (isSaved) return
    setSaving(true)
    try {
      await saveProject(projectId, student.student_id)
      setIsSaved(true)
      toast.success('Project saved for later!')
    } catch {
      toast.error('Failed to save project')
    } finally {
      setSaving(false)
    }
  }, [projectId, student, isSaved])

  const handleComplete = useCallback(async () => {
    if (!student?.student_id) { toast.error('Create a profile first'); return }
    if (isCompleted) return
    setCompleting(true)
    try {
      const r = await completeProject(projectId, student.student_id)
      setIsCompleted(true)
      const newSkills = r.data?.data?.new_skills || []
      if (newSkills.length > 0) {
        toast.success(`Project completed! New skills: ${newSkills.join(', ')}`)
      } else {
        toast.success('Project marked as completed!')
      }
    } catch {
      toast.error('Failed to mark project as completed')
    } finally {
      setCompleting(false)
    }
  }, [projectId, student, isCompleted])

  const handleAddToRoadmap = useCallback(() => {
    setAddedToRoadmap(true)
    toast.success(`${data?.title || 'Project'} added to roadmap!`)
  }, [])

  const handleBackdropClick = useCallback((e) => {
    if (e.target === e.currentTarget) onClose()
  }, [onClose])

  const data = details || project

  if (!data) return null

  const skills = data?.skills_required || []
  const techs = data?.technologies || []
  const outcomes = data?.learning_outcomes || []
  const recommended = recommendedCourses.length > 0 ? recommendedCourses : (data?.recommended_courses || [])
  const prerequisites = data?.prerequisites || []
  const domain = data?.domain || data?.category || ''

  const docLinks = resources?.documentation || []
  const datasets = resources?.datasets || []
  const apiRefs = resources?.api_references || []
  const templates = resources?.starter_templates || []
  const bestPractices = resources?.best_practices || []
  const hasStarterKit = docLinks.length > 0 || datasets.length > 0 || apiRefs.length > 0 || templates.length > 0 || bestPractices.length > 0

  const relatedCourse = recommended?.[0]
  const relatedCourseUrl = relatedCourse?.url || ''

  return (
    <ModalErrorBoundary onClose={onClose}>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-[5vh] sm:pt-[8vh] overflow-y-auto"
            variants={overlay}
            initial="hidden"
            animate="visible"
            exit="exit"
            onClick={handleBackdropClick}
          >
            <motion.div
              className="fixed inset-0 bg-black/50 backdrop-blur-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />

            <motion.div
              ref={modalContentRef}
              className="relative w-full max-w-3xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-800 mb-8 overflow-hidden"
              variants={modalAnim}
              initial="hidden"
              animate="visible"
              exit="exit"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="bg-gradient-to-r from-purple-600 via-purple-500 to-pink-500 px-6 py-5">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <HiOutlineRocketLaunch className="w-4 h-4 text-white/80" />
                      <span className="text-xs font-semibold text-white/80 uppercase tracking-wider">Project</span>
                    </div>
                    <h2 className="text-xl font-bold text-white leading-tight">
                      {data?.title || 'Untitled Project'}
                    </h2>
                    <div className="flex flex-wrap items-center gap-2.5 mt-2.5">
                      {data?.difficulty && (
                        <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${getDifficultyBadgeClasses(data.difficulty)}`}>
                          {data.difficulty}
                        </span>
                      )}
                      {data?.estimated_time && (
                        <span className="flex items-center gap-1 text-sm text-white/80">
                          <HiOutlineClock className="w-3.5 h-3.5" />
                          {data.estimated_time}
                        </span>
                      )}
                      {domain && (
                        <span className="flex items-center gap-1 text-sm text-white/70">
                          <HiOutlineTag className="w-3.5 h-3.5" />
                          {domain}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={onClose}
                    className="p-2 rounded-lg hover:bg-white/15 active:bg-white/20 transition-colors text-white shrink-0 ml-3"
                    aria-label="Close modal"
                  >
                    <HiOutlineXMark className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="px-6 py-6 max-h-[65vh] overflow-y-auto overscroll-contain">
                {!data?.title && !data?.description && !skills.length && !techs.length && (
                  <div className="text-center py-8">
                    <HiOutlineExclamationTriangle className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                    <p className="text-gray-500 dark:text-gray-400 text-sm">No project details available.</p>
                  </div>
                )}

                {data?.description && (
                  <div className="mb-6">
                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed text-[15px]">{data.description}</p>
                  </div>
                )}

                {prerequisites.length > 0 && (
                  <Section icon={HiOutlineShieldCheck} title="Prerequisites" count={prerequisites.length}>
                    <div className="flex flex-wrap gap-1.5">
                      {prerequisites.map((p, i) => (
                        <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 font-medium">
                          {typeof p === 'string' ? p : p?.name || 'Prerequisite'}
                        </span>
                      ))}
                    </div>
                  </Section>
                )}

                <div className="grid sm:grid-cols-2 gap-4 mb-6">
                  {skills.length > 0 && (
                    <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800">
                      <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2.5">
                        Skills Required
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {skills.map((s, i) => (
                          <span key={i} className="text-xs px-2 py-1 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {techs.length > 0 && (
                    <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800">
                      <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2.5">
                        Technologies
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {techs.map((t, i) => (
                          <span key={i} className={`text-xs px-2 py-1 rounded-lg font-medium ${getTechColor(t)}`}>
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {outcomes.length > 0 && (
                  <Section icon={HiOutlineLightBulb} title="Learning Outcomes" count={outcomes.length}>
                    <ul className="space-y-2.5">
                      {outcomes.map((o, i) => (
                        <li key={i} className="flex items-start gap-2.5 text-sm text-gray-600 dark:text-gray-400">
                          <HiOutlineCheckCircle className="w-4.5 h-4.5 text-green-500 shrink-0 mt-0.5" />
                          <span>{o}</span>
                        </li>
                      ))}
                    </ul>
                  </Section>
                )}

                {hasStarterKit && (
                  <Section icon={HiOutlineWrench} title="Project Starter Kit">
                    <div className="space-y-4">
                      {docLinks.length > 0 && (
                        <div>
                          <h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1.5">
                            <HiOutlineBookOpen className="w-3.5 h-3.5" />
                            Documentation
                          </h5>
                          <div className="grid sm:grid-cols-2 gap-2">
                            {docLinks.map((d, i) => <ResourceLink key={i} item={d} />)}
                          </div>
                        </div>
                      )}
                      {datasets.length > 0 && (
                        <div>
                          <h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1.5">
                            <HiOutlineGlobeAlt className="w-3.5 h-3.5" />
                            Datasets
                          </h5>
                          <div className="grid sm:grid-cols-2 gap-2">
                            {datasets.map((d, i) => <ResourceLink key={i} item={d} />)}
                          </div>
                        </div>
                      )}
                      {apiRefs.length > 0 && (
                        <div>
                          <h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1.5">
                            <HiOutlineGlobeAlt className="w-3.5 h-3.5" />
                            API References
                          </h5>
                          <div className="grid sm:grid-cols-2 gap-2">
                            {apiRefs.map((d, i) => <ResourceLink key={i} item={d} />)}
                          </div>
                        </div>
                      )}
                      {templates.length > 0 && (
                        <div>
                          <h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1.5">
                            <HiOutlineWrench className="w-3.5 h-3.5" />
                            Starter Templates
                          </h5>
                          <div className="grid sm:grid-cols-2 gap-2">
                            {templates.map((d, i) => <ResourceLink key={i} item={d} />)}
                          </div>
                        </div>
                      )}
                      {bestPractices.length > 0 && (
                        <div>
                          <h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1.5">
                            <HiOutlineShieldCheck className="w-3.5 h-3.5" />
                            Best Practices
                          </h5>
                          <ul className="space-y-2">
                            {bestPractices.map((p, i) => (
                              <li key={i} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
                                <HiOutlineCheckCircle className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                                <span>{typeof p === 'string' ? p : p?.text || 'Best practice'}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </Section>
                )}

                {recommended.length > 0 && (
                  <Section icon={HiOutlineAcademicCap} title="Recommended Courses" count={recommended.length}>
                    <div className="space-y-3">
                      {recommended.slice(0, 3).map((course, i) => (
                        <CourseCard key={course?.id || i} course={course} />
                      ))}
                    </div>
                  </Section>
                )}

                {student && (
                  <Section icon={HiOutlineSparkles} title="AI Mentor Recommendation">
                    <div className="p-4 rounded-xl bg-gradient-to-r from-accent-50 to-primary-50 dark:from-accent-900/20 dark:to-primary-900/20 border border-accent-100 dark:border-accent-900/30">
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                        {isCompleted ? (
                          <>Great job completing this project! Check your dashboard for updated progress and skill mastery.</>
                        ) : recommended.length > 0 ? (
                          <>
                            Based on your profile, we recommend completing{' '}
                            <strong>{recommended[0]?.title}</strong> before attempting this project.
                            Estimated readiness: <strong>{Math.round((recommended[0]?._match_score || 0) * 100)}%</strong> skill coverage.
                          </>
                        ) : (
                          <>This project matches your current skill level well. Start building to strengthen your portfolio!</>
                        )}
                      </p>
                    </div>
                  </Section>
                )}
              </div>

              <div className="px-6 py-4 border-t border-gray-100 dark:border-gray-800 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <div className="flex flex-wrap gap-2 flex-1">
                  <button
                    onClick={handleSave}
                    disabled={saving || isSaved}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                      isSaved
                        ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 cursor-default'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                    } ${saving ? 'opacity-60 cursor-wait' : ''}`}
                  >
                    <HiOutlineStar className="w-4 h-4" />
                    {saving ? 'Saving...' : isSaved ? 'Saved' : 'Save for Later'}
                  </button>

                  <button
                    onClick={handleAddToRoadmap}
                    disabled={addedToRoadmap}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                      addedToRoadmap
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 cursor-default'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                    }`}
                  >
                    {addedToRoadmap ? <HiOutlineCheckCircle className="w-4 h-4" /> : <HiOutlinePlus className="w-4 h-4" />}
                    {addedToRoadmap ? 'Added' : 'Add to Roadmap'}
                  </button>

                  {relatedCourseUrl && (
                    <a
                      href={relatedCourseUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all"
                    >
                      <HiOutlineBookOpen className="w-4 h-4" />
                      Visit Course
                      <HiOutlineArrowTopRightOnSquare className="w-3.5 h-3.5 opacity-60" />
                    </a>
                  )}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={handleComplete}
                    disabled={completing || isCompleted}
                    className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                      isCompleted
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 cursor-default'
                        : 'bg-gradient-to-r from-purple-500 to-pink-600 text-white hover:opacity-90 active:scale-[0.97] shadow-sm hover:shadow-md'
                    } ${completing ? 'opacity-60 cursor-wait' : ''}`}
                  >
                    <HiOutlineCheckCircle className="w-4 h-4" />
                    {completing ? 'Saving...' : isCompleted ? 'Completed' : 'Mark Complete'}
                  </button>

                  <button
                    onClick={onClose}
                    className="px-4 py-2.5 rounded-xl text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </ModalErrorBoundary>
  )
})

export default ProjectDetailsModal
