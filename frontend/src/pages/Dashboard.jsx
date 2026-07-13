import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  HiOutlineUser, HiOutlineMap, HiOutlineChatBubbleLeftEllipsis, HiOutlineBookOpen,
  HiOutlineArrowRight, HiOutlineBolt, HiOutlineFire, HiOutlineClock,
  HiOutlineAcademicCap, HiOutlineChartBarSquare,
} from 'react-icons/hi2'
import { useApp } from '../context/AppContext'
import { SkeletonCard } from '../components/common/SkeletonLoader'
import EmptyState from '../components/common/EmptyState'
import { skillLevelColor } from '../utils/helpers'

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
  const { student, roadmap, loading, fetchRoadmap, courses } = useApp()

  useEffect(() => {
    if (student?.student_id) fetchRoadmap()
  }, [student, fetchRoadmap])

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
          action={() => {}}
          actionLabel="Create Profile"
        />
        <div className="text-center mt-4">
          <Link to="/profile" className="btn-primary">Create Profile</Link>
        </div>
      </div>
    )
  }

  const weeks = roadmap?.weeks || []
  const completedWeeks = weeks.filter((w) => w.completed).length
  const totalHours = weeks.reduce((sum, w) => sum + (w.estimated_hours || 0), 0)
  const nextWeek = weeks.find((w) => !w.completed)

  return (
    <div className="page-container">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        {/* Header */}
        <motion.div variants={fadeUp} className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-display font-bold mb-2">
            Welcome back, <span className="gradient-text">{student.name}</span>
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            {student.career_goal || 'Set your career goal to personalise your experience'}
          </p>
        </motion.div>

        {/* Stats */}
        <motion.div variants={fadeUp} className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard icon={HiOutlineUser} label="Skill Level" value={student.skill_level} color="bg-blue-100 dark:bg-blue-900/30 text-blue-600" to="/profile" />
          <StatCard icon={HiOutlineMap} label="Roadmap Weeks" value={`${completedWeeks}/${weeks.length || '—'}`} color="bg-purple-100 dark:bg-purple-900/30 text-purple-600" to="/roadmap" />
          <StatCard icon={HiOutlineClock} label="Study Hours" value={`${totalHours}h`} color="bg-green-100 dark:bg-green-900/30 text-green-600" to="/progress" />
          <StatCard icon={HiOutlineFire} label="Skills" value={`${student.current_skills?.length || 0} mastered`} color="bg-orange-100 dark:bg-orange-900/30 text-orange-600" to="/profile" />
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <motion.div variants={fadeUp} className="lg:col-span-1 space-y-4">
            <h2 className="text-lg font-semibold">Quick Actions</h2>
            {[
              { to: '/roadmap', icon: HiOutlineMap, label: 'View Roadmap', color: 'bg-primary-50 dark:bg-primary-900/30 text-primary-600' },
              { to: '/chat', icon: HiOutlineChatBubbleLeftEllipsis, label: 'Chat with AI Mentor', color: 'bg-accent-50 dark:bg-accent-900/30 text-accent-600' },
              { to: '/resources', icon: HiOutlineBookOpen, label: 'Browse Resources', color: 'bg-green-50 dark:bg-green-900/30 text-green-600' },
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

        {/* Skills */}
        {student.current_skills?.length > 0 && (
          <motion.div variants={fadeUp} className="mt-8">
            <h2 className="text-lg font-semibold mb-4">Your Skills</h2>
            <div className="flex flex-wrap gap-2">
              {student.current_skills.map((skill, i) => (
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
