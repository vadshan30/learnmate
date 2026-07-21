import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import {
  HiOutlineCalendarDays, HiOutlineViewColumns, HiOutlineChartBar,
  HiOutlineSparkles, HiOutlinePlus,
} from 'react-icons/hi2'
import { useApp } from '../context/AppContext'
import { SkeletonCard } from '../components/common/SkeletonLoader'
import StudyPlannerDashboard from '../components/study/StudyPlannerDashboard'
import StudyGoalCard from '../components/study/StudyGoalCard'
import WeeklyPlanner from '../components/study/WeeklyPlanner'
import CalendarView from '../components/study/CalendarView'
import StudySessionCard from '../components/study/StudySessionCard'
import SessionModal from '../components/study/SessionModal'
import StudyAnalytics from '../components/study/StudyAnalytics'
import UpcomingSessions from '../components/study/UpcomingSessions'
import ReminderSettings from '../components/study/ReminderSettings'
import { optimizeStudySchedule } from '../services/studyPlannerApi'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.08 } } }

const TABS = [
  { key: 'dashboard', label: 'Dashboard', icon: HiOutlineCalendarDays },
  { key: 'weekly', label: 'Weekly Planner', icon: HiOutlineViewColumns },
  { key: 'calendar', label: 'Calendar', icon: HiOutlineCalendarDays },
  { key: 'analytics', label: 'Analytics', icon: HiOutlineChartBar },
]

export default function StudyPlanner() {
  const {
    student, studySessions, studyGoal, studyAnalytics, studyDashboard,
    loading, fetchAllStudyData,
    createStudySession, updateStudySession, deleteStudySession, completeStudySession,
    saveStudyGoal, generateSessionsFromRoadmap, roadmap,
  } = useApp()

  const [activeTab, setActiveTab] = useState('dashboard')
  const [modalOpen, setModalOpen] = useState(false)
  const [editingSession, setEditingSession] = useState(null)
  const [aiRecommendations, setAiRecommendations] = useState(null)
  const [loadingAI, setLoadingAI] = useState(false)

  useEffect(() => {
    if (student?.student_id) {
      fetchAllStudyData()
    }
  }, [student, fetchAllStudyData])

  const handleCreateSession = useCallback(async (data) => {
    await createStudySession(data)
    setModalOpen(false)
    setEditingSession(null)
  }, [createStudySession])

  const handleUpdateSession = useCallback(async (data) => {
    if (editingSession?.id) {
      await updateStudySession(editingSession.id, data)
    }
    setModalOpen(false)
    setEditingSession(null)
  }, [editingSession, updateStudySession])

  const handleEditSession = useCallback((session) => {
    setEditingSession(session)
    setModalOpen(true)
  }, [])

  const handleCompleteSession = useCallback(async (sessionId) => {
    await completeStudySession(sessionId)
    fetchAllStudyData()
  }, [completeStudySession, fetchAllStudyData])

  const handleDeleteSession = useCallback(async (sessionId) => {
    await deleteStudySession(sessionId)
    fetchAllStudyData()
  }, [deleteStudySession, fetchAllStudyData])

  const handleSaveGoal = useCallback(async (data) => {
    await saveStudyGoal(data)
  }, [saveStudyGoal])

  const handleGenerateFromRoadmap = useCallback(async () => {
    if (!roadmap) return
    await generateSessionsFromRoadmap({
      weekly_hours: studyGoal?.weekly_goal_hours || 10,
      preferred_days: studyGoal?.preferred_days?.length ? studyGoal.preferred_days : ['Monday', 'Wednesday', 'Friday'],
    })
    fetchAllStudyData()
  }, [roadmap, studyGoal, generateSessionsFromRoadmap, fetchAllStudyData])

  const handleOptimize = useCallback(async () => {
    if (!student?.student_id) return
    setLoadingAI(true)
    try {
      const r = await optimizeStudySchedule(student.student_id)
      setAiRecommendations(r.data?.data?.recommendations || 'No recommendations available.')
    } catch {
      setAiRecommendations('Failed to get recommendations. Please try again.')
    } finally {
      setLoadingAI(false)
    }
  }, [student])

  const handleOpenModal = useCallback(() => {
    setEditingSession(null)
    setModalOpen(true)
  }, [])

  if (loading.student) {
    return (
      <div className="page-container">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => <SkeletonCard key={i} />)}
        </div>
      </div>
    )
  }

  if (!student) {
    return (
      <div className="page-container">
        <div className="glass-card p-8 text-center">
          <p className="text-gray-500 mb-4">Create a student profile first to use the Study Planner.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        {/* Header */}
        <motion.div variants={fadeUp} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-display font-bold">
              Study <span className="gradient-text">Planner</span>
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              Organize, schedule, and track your learning journey
            </p>
          </div>
          <div className="flex gap-2">
            {roadmap && (
              <button
                onClick={handleGenerateFromRoadmap}
                className="btn-secondary text-sm flex items-center gap-1.5"
              >
                <HiOutlineSparkles className="w-4 h-4" />
                Generate from Roadmap
              </button>
            )}
            <button onClick={handleOpenModal} className="btn-primary text-sm flex items-center gap-1.5">
              <HiOutlinePlus className="w-4 h-4" />
              New Session
            </button>
          </div>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div variants={fadeUp} className="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-xl p-1 mb-6 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                activeTab === tab.key
                  ? 'bg-white dark:bg-gray-700 shadow-sm text-primary-600 dark:text-primary-400'
                  : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </motion.div>

        {/* Tab Content */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <StudyPlannerDashboard dashboard={studyDashboard} />
            <div className="grid lg:grid-cols-2 gap-6">
              <StudyGoalCard goal={studyGoal} onSave={handleSaveGoal} />
              <UpcomingSessions sessions={studySessions} onStartSession={handleEditSession} />
            </div>
            <ReminderSettings sessions={studySessions} />
            {/* AI Recommendations */}
            <motion.div variants={fadeUp} className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <HiOutlineSparkles className="w-5 h-5 text-purple-500" />
                  AI Schedule Optimization
                </h3>
                <button
                  onClick={handleOptimize}
                  disabled={loadingAI}
                  className="btn-secondary text-sm"
                >
                  {loadingAI ? 'Analyzing...' : 'Get Recommendations'}
                </button>
              </div>
              {aiRecommendations ? (
                <div className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap prose prose-sm max-w-none">
                  {aiRecommendations}
                </div>
              ) : (
                <p className="text-sm text-gray-500">Click "Get Recommendations" to let AI analyze your schedule.</p>
              )}
            </motion.div>
          </div>
        )}

        {activeTab === 'weekly' && (
          <WeeklyPlanner
            sessions={studySessions}
            onComplete={handleCompleteSession}
            onDelete={handleDeleteSession}
            onEdit={handleEditSession}
            onAddSession={handleOpenModal}
          />
        )}

        {activeTab === 'calendar' && (
          <CalendarView
            sessions={studySessions}
            onEventClick={handleEditSession}
          />
        )}

        {activeTab === 'analytics' && (
          <StudyAnalytics analytics={studyAnalytics} />
        )}
      </motion.div>

      {/* Session Modal */}
      <SessionModal
        open={modalOpen}
        onClose={() => { setModalOpen(false); setEditingSession(null) }}
        onSave={editingSession?.id ? handleUpdateSession : handleCreateSession}
        session={editingSession}
      />
    </div>
  )
}
