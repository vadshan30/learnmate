import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  HiOutlineUser, HiOutlineMap, HiOutlineBookOpen,
  HiOutlineArrowRight, HiOutlineFire, HiOutlineClock,
  HiOutlineAcademicCap, HiOutlineChartBarSquare, HiOutlineBriefcase,
  HiOutlineCheckCircle, HiOutlineCalendarDays, HiOutlineSparkles,
  HiOutlineArrowPath,
} from 'react-icons/hi2'
import { useApp } from '../context/AppContext'
import { useAuth } from '../context/AuthContext'
import { getProjectStats, getCareerTestHistory } from '../services/api'
import { SkeletonCard } from '../components/common/SkeletonLoader'
import EmptyState from '../components/common/EmptyState'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.08 } } }

function StatCard({ icon: Icon, label, value, color, to }) {
  return (
    <motion.div variants={fadeUp} whileHover={{ y: -2 }}>
      <Link to={to} className="glass-card p-5 flex items-center gap-4 group block">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
          <p className="text-xl font-bold truncate">{value || '—'}</p>
        </div>
        <HiOutlineArrowRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
      </Link>
    </motion.div>
  )
}

export default function Dashboard() {
  const { student, roadmap, progress, loading, fetchRoadmap, fetchProgress, studySessions, studyGoal, fetchAllStudyData } = useApp()
  const { user } = useAuth()
  const [projectStats, setProjectStats] = useState(null)
  const [careerResult, setCareerResult] = useState(null)

  const firstName = (user?.full_name || student?.name || 'there').split(' ')[0]
  const userId = user?.id || localStorage.getItem('learnmate_guest_id') || 'guest'

  useEffect(() => {
    if (student?.student_id) {
      fetchRoadmap()
      fetchProgress()
      fetchAllStudyData()
      getProjectStats(student.student_id)
        .then((r) => setProjectStats(r.data?.data || null))
        .catch(() => {})
    }
    // Load career test history for dashboard widget
    getCareerTestHistory(userId)
      .then((r) => {
        const history = r.data?.data || []
        if (history.length > 0) setCareerResult(history[0])
      })
      .catch(() => {})
  }, [student, fetchRoadmap, fetchProgress, fetchAllStudyData, userId])

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
        <EmptyState
          icon={HiOutlineUser}
          title="No profile yet"
          description="Create your student profile to get started with personalised learning."
        />
        <div className="text-center mt-4">
          <Link to="/profile" className="btn-primary">Create Profile</Link>
        </div>
      </div>
    )
  }

  const weeks = roadmap?.weeks || []
  const totalWeeks = weeks.length || roadmap?.progress?.total_weeks || 10
  const completedWeeks = progress?.completed_weeks ?? weeks.filter((w) => w.completed).length
  const overallProgress = progress?.overall_progress ?? roadmap?.progress?.percentage ?? 0
  const totalHours = weeks.reduce((sum, w) => sum + (w.estimated_hours || 0), 0)
  const completedTopics = progress?.completed_topics ?? roadmap?.completed_topics?.length ?? 0
  const totalTopics = progress?.total_topics ?? roadmap?.total_topics ?? 0
  const nextWeek = weeks.find((w) => !w.completed && w.completion_status !== 'completed')
  const skills = student.current_skills || []
  const certs = roadmap?.certifications || []
  const proj = roadmap?.final_project

  return (
    <div className="page-container">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        {/* Header */}
        <motion.div variants={fadeUp} className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-display font-bold mb-2">
            Welcome back, <span className="gradient-text">{firstName}</span>
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            {student.career_goal || 'Set your career goal to personalise your experience'}
          </p>
        </motion.div>

        {/* Stats */}
        <motion.div variants={fadeUp} className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard icon={HiOutlineUser} label="Skill Level" value={student.skill_level} color="bg-blue-100 dark:bg-blue-900/30 text-blue-600" to="/profile" />
          <StatCard icon={HiOutlineChartBarSquare} label="Overall Progress" value={`${Math.round(overallProgress)}%`} color="bg-purple-100 dark:bg-purple-900/30 text-purple-600" to="/progress" />
          <StatCard icon={HiOutlineClock} label="Study Hours" value={`${totalHours}h`} color="bg-green-100 dark:bg-green-900/30 text-green-600" to="/progress" />
          <StatCard icon={HiOutlineFire} label="Skills" value={`${skills.length} mastered`} color="bg-orange-100 dark:bg-orange-900/30 text-orange-600" to="/profile" />
        </motion.div>

        {/* Study Planner Section */}
        <motion.div variants={fadeUp} className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <HiOutlineCalendarDays className="w-5 h-5 text-primary-500" />
              Today&apos;s Study Sessions
            </h2>
            <Link to="/study-planner" className="text-sm font-medium text-primary-600 hover:text-primary-700 flex items-center gap-1">
              View Planner <HiOutlineArrowRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Today's Sessions Count */}
            <div className="glass-card p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Today&apos;s Sessions</p>
              <p className="text-2xl font-bold">
                {(studySessions || []).filter((s) => {
                  const today = new Date().toISOString().split('T')[0]
                  return s.date === today && s.status !== 'completed'
                }).length || 0}
              </p>
            </div>
            {/* Weekly Goal Progress */}
            <div className="glass-card p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Weekly Goal</p>
              <div className="flex items-center gap-2">
                <p className="text-2xl font-bold">{studyGoal?.weekly_goal_hours || 10}h</p>
                <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full gradient-bg rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.min(
                        ((studySessions || []).filter((s) => {
                          const now = new Date()
                          const monday = new Date(now)
                          monday.setDate(now.getDate() - now.getDay() + 1)
                          const sunday = new Date(monday)
                          sunday.setDate(monday.getDate() + 6)
                          return s.date >= monday.toISOString().split('T')[0] &&
                            s.date <= sunday.toISOString().split('T')[0] &&
                            s.status === 'completed'
                        }).reduce((sum, s) => sum + (s.duration || 0), 0) / (studyGoal?.weekly_goal_hours || 10)) * 100, 100)}%`
                    }}
                  />
                </div>
              </div>
            </div>
            {/* Next Session Countdown */}
            <div className="glass-card p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Next Session</p>
              {(() => {
                const upcoming = (studySessions || [])
                  .filter((s) => s.status === 'scheduled' && s.date >= new Date().toISOString().split('T')[0])
                  .sort((a, b) => `${a.date}T${a.start_time}`.localeCompare(`${b.date}T${b.start_time}`))[0]
                return upcoming ? (
                  <div>
                    <p className="text-sm font-medium truncate">{upcoming.title}</p>
                    <p className="text-xs text-gray-500">{upcoming.date} · {upcoming.start_time}</p>
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">No upcoming sessions</p>
                )
              })()}
            </div>
            {/* Quick Start */}
            <Link to="/study-planner" className="glass-card p-4 flex items-center gap-3 group hover:shadow-md transition-all block">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-primary-100 dark:bg-primary-900/30 text-primary-600">
                <HiOutlineCalendarDays className="w-5 h-5" />
              </div>
              <span className="font-medium flex-1 text-sm">Open Study Planner</span>
              <HiOutlineArrowRight className="w-4 h-4 text-gray-400 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </motion.div>

        {/* Career Test Section */}
        <motion.div variants={fadeUp} className="mb-8">
          {careerResult ? (
            <div className="glass-card p-5">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shrink-0">
                  <HiOutlineAcademicCap className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold">Career Match</h3>
                    <span className="text-sm font-bold text-primary-600">
                      {careerResult.top_careers?.[0]?.career_name}
                    </span>
                    <span className="text-xs font-bold text-primary-500">
                      {Math.round(careerResult.top_careers?.[0]?.percentage || 0)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                    <span>Last test: {careerResult.created_at ? new Date(careerResult.created_at).toLocaleDateString() : 'Unknown'}</span>
                    {careerResult.top_careers?.length > 1 && (
                      <span>Also: {careerResult.top_careers.slice(1, 3).map(c => c.career_name).join(', ')}</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Link to="/career-test" className="btn-secondary text-sm flex items-center gap-1">
                    <HiOutlineArrowPath className="w-4 h-4" /> Retake
                  </Link>
                  <Link to="/career-test" className="btn-primary text-sm flex items-center gap-1">
                    Details <HiOutlineArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-card p-5 flex flex-col sm:flex-row items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shrink-0">
                <HiOutlineAcademicCap className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1 text-center sm:text-left">
                <h3 className="font-semibold">Career Aptitude Test</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Discover your ideal tech career path with AI-powered analysis
                </p>
              </div>
              <Link
                to="/career-test"
                className="btn-primary text-sm flex items-center gap-1 shrink-0"
              >
                Take Test <HiOutlineArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}
        </motion.div>

        {/* Learning Journey Stats */}
        <motion.div variants={fadeUp} className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[
            { icon: HiOutlineBookOpen, label: 'Courses', value: projectStats?.total_courses || '—', sub: 'Available', color: 'text-blue-500' },
            { icon: HiOutlineBriefcase, label: 'Projects Done', value: projectStats?.completed_count ?? '—', sub: `of ${projectStats?.total_projects || 12}`, color: 'text-purple-500' },
            { icon: HiOutlineCheckCircle, label: 'Completed', value: completedTopics, sub: `of ${totalTopics} topics`, color: 'text-green-500' },
            { icon: HiOutlineAcademicCap, label: 'Certs', value: certs.length, sub: 'Recommended', color: 'text-emerald-500' },
          ].map((s, i) => (
            <div key={i} className="glass-card p-4 flex items-center gap-3">
              <s.icon className={`w-5 h-5 ${s.color} shrink-0`} />
              <div className="min-w-0">
                <p className="text-xl font-bold">{s.value}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{s.label}</p>
              </div>
            </div>
          ))}
        </motion.div>

        {/* Progress bar */}
        {roadmap && (
          <motion.div variants={fadeUp} className="glass-card p-5 mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Roadmap Progress</span>
              <span className="text-sm text-gray-500">{completedWeeks}/{totalWeeks} weeks • {completedTopics}/{totalTopics} topics ({Math.round(overallProgress)}%)</span>
            </div>
            <div className="w-full h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <motion.div
                className="h-full gradient-bg rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${overallProgress}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
              />
            </div>
          </motion.div>
        )}

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <motion.div variants={fadeUp} className="lg:col-span-1 space-y-4">
            <h2 className="text-lg font-semibold">Quick Actions</h2>
            {[
              { to: '/roadmap', icon: HiOutlineMap, label: 'View Roadmap', color: 'bg-primary-50 dark:bg-primary-900/30 text-primary-600' },
              { to: '/resources', icon: HiOutlineBookOpen, label: 'Browse Resources', color: 'bg-green-50 dark:bg-green-900/30 text-green-600' },
              { to: '/career-test', icon: HiOutlineAcademicCap, label: careerResult ? 'Retake Career Test' : 'Take Career Test', color: 'bg-amber-50 dark:bg-amber-900/30 text-amber-600' },
            ].map((a) => (
              <Link key={a.to} to={a.to} className="glass-card p-4 flex items-center gap-3 group hover:shadow-md transition-all block">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${a.color}`}>
                  <a.icon className="w-5 h-5" />
                </div>
                <span className="font-medium flex-1">{a.label}</span>
                <HiOutlineArrowRight className="w-4 h-4 text-gray-400 group-hover:translate-x-1 transition-transform" />
              </Link>
            ))}
          </motion.div>

          {/* Next Week */}
          <motion.div variants={fadeUp} className="lg:col-span-2">
            <h2 className="text-lg font-semibold mb-4">Upcoming</h2>
            {nextWeek ? (
              <div className="glass-card p-6">
                <div className="flex items-center gap-3 mb-4">
                  <span className="badge-purple">Week {nextWeek.week_number || '?'}</span>
                  <span className="text-sm text-gray-500">{nextWeek.estimated_hours || 0}h estimated</span>
                </div>
                <h3 className="text-xl font-semibold mb-3">{nextWeek.title || 'Continue Learning'}</h3>
                {nextWeek.topics?.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {nextWeek.topics.map((t, i) => (
                      <span key={i} className="badge-blue text-xs">{t}</span>
                    ))}
                  </div>
                )}
                {nextWeek.projects?.length > 0 && (
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-medium">Projects:</span> {nextWeek.projects.join(', ')}
                  </div>
                )}
                <Link to="/roadmap" className="inline-flex items-center gap-1 mt-4 text-sm font-medium text-primary-600 hover:text-primary-700">
                  View full roadmap <HiOutlineArrowRight className="w-4 h-4" />
                </Link>
              </div>
            ) : (
              <div className="glass-card p-8 text-center">
                <HiOutlineMap className="w-10 h-10 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500 mb-4">No roadmap yet. Generate one to start learning!</p>
                <Link to="/roadmap" className="btn-primary text-sm">Generate Roadmap</Link>
              </div>
            )}
          </motion.div>
        </div>

        {/* Recommended Certifications */}
        {certs.length > 0 && (
          <motion.div variants={fadeUp} className="mt-8">
            <h2 className="text-lg font-semibold mb-4">Recommended Certifications</h2>
            <div className="flex flex-wrap gap-2">
              {certs.slice(0, 5).map((c, i) => (
                <span key={i} className="badge-purple">
                  {typeof c === 'string' ? c : c.name || 'Certification'}
                </span>
              ))}
            </div>
          </motion.div>
        )}

        {/* Final Project */}
        {proj && (
          <motion.div variants={fadeUp} className="mt-6">
            <h2 className="text-lg font-semibold mb-4">Capstone Project</h2>
            <div className="glass-card p-4">
              <p className="font-medium">{proj.title || 'Final Project'}</p>
              {proj.description && <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{proj.description}</p>}
            </div>
          </motion.div>
        )}

        {/* Skills */}
        {skills.length > 0 && (
          <motion.div variants={fadeUp} className="mt-8">
            <h2 className="text-lg font-semibold mb-4">Your Skills</h2>
            <div className="flex flex-wrap gap-2">
              {skills.map((skill, i) => (
                <span key={i} className="badge-blue">{skill}</span>
              ))}
            </div>
          </motion.div>
        )}

        {/* Interests */}
        {student.interests?.length > 0 && (
          <motion.div variants={fadeUp} className="mt-6">
            <h2 className="text-lg font-semibold mb-4">Interests</h2>
            <div className="flex flex-wrap gap-2">
              {student.interests.map((interest, i) => (
                <span key={i} className="badge-purple">{interest}</span>
              ))}
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}
