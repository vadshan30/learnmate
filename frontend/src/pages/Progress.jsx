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
  const { student, roadmap, courses, projects, certifications } = useApp()

  const weeks = roadmap?.weeks || []
  const completedWeeks = weeks.filter((w) => w.completed).length
  const totalHours = weeks.reduce((sum, w) => sum + (w.estimated_hours || 0), 0)
  const skills = student?.current_skills || []

  const weeklyData = useMemo(() => {
    return weeks.map((w, i) => ({
      name: `W${w.week_number || i + 1}`,
      hours: w.estimated_hours || 0,
      completed: w.completed ? 1 : 0,
      topics: w.topics?.length || 0,
    }))
  }, [weeks])

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

  const progressPct = weeks.length ? Math.round((completedWeeks / weeks.length) * 100) : 0

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
          <StatCard icon={HiOutlineAcademicCap} label="Completion" value={`${progressPct}%`} color="bg-primary-100 dark:bg-primary-900/30 text-primary-600" />
          <StatCard icon={HiOutlineClock} label="Study Hours" value={`${totalHours}h`} color="bg-green-100 dark:bg-green-900/30 text-green-600" />
          <StatCard icon={HiOutlineFire} label="Skills" value={skills.length} color="bg-orange-100 dark:bg-orange-900/30 text-orange-600" />
          <StatCard icon={HiOutlineChartBar} label="Weeks Done" value={`${completedWeeks}/${weeks.length || '—'}`} color="bg-purple-100 dark:bg-purple-900/30 text-purple-600" />
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
                  <Area type="monotone" dataKey="hours" stroke="#3b82f6" fill="#3b82f620" strokeWidth={2} />
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
