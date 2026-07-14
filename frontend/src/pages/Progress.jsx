import { useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { HiOutlineChartBar, HiOutlineClock, HiOutlineFire, HiOutlineAcademicCap } from 'react-icons/hi2'
import { useApp } from '../context/AppContext'
import EmptyState from '../components/common/EmptyState'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.08 } } }

const COLORS = ['#3b82f6', '#a855f7', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4']

function ChartCard({ title, children, className = '' }) {
  return (
    <motion.div variants={fadeUp} className={`glass-card p-5 ${className}`}>
      <h3 className="font-semibold text-sm mb-4">{title}</h3>
      {children}
    </motion.div>
  )
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <motion.div variants={fadeUp} className="glass-card p-5 flex items-center gap-3">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-xl font-bold">{value}</p>
      </div>
    </motion.div>
  )
}

export default function Progress() {
  const { student, roadmap, progress, fetchProgress, courses, projects, certifications } = useApp()

  useEffect(() => {
    if (student?.student_id) fetchProgress()
  }, [student, fetchProgress])

  const weeks = roadmap?.weeks || []
  const skills = student?.current_skills || []

  // Use backend progress data if available
  const overallProgress = progress?.overall_progress ?? roadmap?.progress?.percentage ?? 0
  const completedWeeks = progress?.completed_weeks ?? weeks.filter((w) => w.completed || w.completion_status === 'completed').length
  const totalTopics = progress?.total_topics ?? roadmap?.total_topics ?? 0
  const completedTopics = progress?.completed_topics ?? roadmap?.completed_topics?.length ?? 0
  const totalHours = weeks.reduce((sum, w) => sum + (w.estimated_hours || 0), 0)
  const remainingHours = progress?.remaining_hours ?? totalHours
  const certCount = roadmap?.certifications?.length ?? certifications.length

  const weeklyData = useMemo(() => {
    // Use backend week_progress if available
    if (progress?.week_progress?.length > 0) {
      return progress.week_progress.map((wp) => ({
        name: `W${wp.week_number}`,
        percentage: wp.percentage || 0,
        completed: wp.completed ? 1 : 0,
        topics: wp.total_topics || 0,
        completedTopics: wp.completed_topics_count || 0,
      }))
    }
    return weeks.map((w, i) => ({
      name: `W${w.week_number || i + 1}`,
      percentage: w.completed || w.completion_status === 'completed' ? 100 : 0,
      completed: w.completed || w.completion_status === 'completed' ? 1 : 0,
      topics: w.topics?.length || 0,
      completedTopics: 0,
    }))
  }, [weeks, progress])

  const skillData = useMemo(() => {
    const groups = { frontend: 0, backend: 0, data: 0, devops: 0, other: 0 }
    skills.forEach((s) => {
      const l = s.toLowerCase()
      if (['react', 'vue', 'angular', 'html', 'css', 'javascript', 'typescript', 'frontend'].some((k) => l.includes(k))) groups.frontend++
      else if (['python', 'java', 'node', 'go', 'rust', 'sql', 'backend', 'api'].some((k) => l.includes(k))) groups.backend++
      else if (['machine learning', 'data', 'tensor', 'pandas', 'ai', 'ml', 'analysis'].some((k) => l.includes(k))) groups.data++
      else if (['docker', 'kubernetes', 'aws', 'cloud', 'linux', 'devops', 'ci/cd'].some((k) => l.includes(k))) groups.devops++
      else groups.other++
    })
    return Object.entries(groups).filter(([, v]) => v > 0).map(([k, v]) => ({ name: k, value: v }))
  }, [skills])

  if (!student) {
    return (
      <div className="page-container">
        <EmptyState icon={HiOutlineChartBar} title="No data yet" description="Create a profile and generate a roadmap to see your progress analytics." />
      </div>
    )
  }

  return (
    <div className="page-container">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        <motion.div variants={fadeUp} className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-display font-bold mb-2">Progress Analytics</h1>
          <p className="text-gray-500 dark:text-gray-400">Track your learning journey</p>
        </motion.div>

        {/* Stats */}
        <motion.div variants={fadeUp} className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard icon={HiOutlineAcademicCap} label="Completion" value={`${Math.round(overallProgress)}%`} color="bg-primary-100 dark:bg-primary-900/30 text-primary-600" />
          <StatCard icon={HiOutlineClock} label="Study Hours" value={`${totalHours}h`} color="bg-green-100 dark:bg-green-900/30 text-green-600" />
          <StatCard icon={HiOutlineFire} label="Skills" value={skills.length} color="bg-orange-100 dark:bg-orange-900/30 text-orange-600" />
          <StatCard icon={HiOutlineChartBar} label="Topics Done" value={`${completedTopics}/${totalTopics || '—'}`} color="bg-purple-100 dark:bg-purple-900/30 text-purple-600" />
        </motion.div>

        {/* Extra stats row */}
        <motion.div variants={fadeUp} className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard icon={HiOutlineAcademicCap} label="Weeks Done" value={`${completedWeeks}/${weeks.length || '—'}`} color="bg-blue-100 dark:bg-blue-900/30 text-blue-600" />
          <StatCard icon={HiOutlineClock} label="Remaining" value={`${Math.round(remainingHours)}h`} color="bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600" />
          <StatCard icon={HiOutlineFire} label="Certifications" value={certCount} color="bg-pink-100 dark:bg-pink-900/30 text-pink-600" />
          <StatCard icon={HiOutlineChartBar} label="Status" value={progress?.completion_status?.replace('_', ' ') || 'Not started'} color="bg-gray-100 dark:bg-gray-800 text-gray-600" />
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Weekly Progress Chart */}
          <ChartCard title="Weekly Progress">
            {weeklyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Area type="monotone" dataKey="percentage" stroke="#3b82f6" fill="#3b82f620" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400 text-center py-10">Generate a roadmap to see data</p>
            )}
          </ChartCard>

          {/* Topics per Week */}
          <ChartCard title="Topics per Week">
            {weeklyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="topics" fill="#a855f7" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400 text-center py-10">No data available</p>
            )}
          </ChartCard>
        </div>

        {/* Skill Distribution */}
        {skillData.length > 0 && (
          <ChartCard title="Skill Distribution" className="max-w-lg">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={skillData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                  {skillData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        )}
      </motion.div>
    </div>
  )
}
