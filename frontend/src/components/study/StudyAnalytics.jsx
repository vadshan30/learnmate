import { useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend,
} from 'recharts'
import {
  HiOutlineChartBar, HiOutlineFire, HiOutlineClock, HiOutlineCheckCircle,
  HiOutlineAcademicCap, HiOutlineSun, HiOutlineCalendarDays, HiOutlineTrophy,
} from 'react-icons/hi2'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

const PIE_COLORS = ['#3b82f6', '#22c55e', '#eab308', '#a855f7', '#ef4444']
const PIE_LABELS = { scheduled: 'Scheduled', completed: 'Completed', in_progress: 'In Progress', skipped: 'Skipped', missed: 'Missed' }

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="glass-card p-4 flex items-center gap-3">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="min-w-0">
        <p className="text-xl font-bold">{value}</p>
        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{label}</p>
      </div>
    </div>
  )
}

export default function StudyAnalytics({ analytics }) {
  const pieData = useMemo(() => {
    if (!analytics?.status_distribution) return []
    return Object.entries(analytics.status_distribution).map(([key, val]) => ({
      name: PIE_LABELS[key] || key,
      value: val,
    }))
  }, [analytics])

  if (!analytics) {
    return (
      <div className="glass-card p-8 text-center">
        <HiOutlineChartBar className="w-10 h-10 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-500">No analytics data yet. Complete some study sessions!</p>
      </div>
    )
  }

  return (
    <motion.div variants={fadeUp} className="space-y-6">
      <h3 className="text-lg font-semibold">Study Analytics</h3>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={HiOutlineClock} label="Weekly Hours" value={`${analytics.weekly_hours || 0}h`} color="bg-blue-100 dark:bg-blue-900/30 text-blue-600" />
        <StatCard icon={HiOutlineCalendarDays} label="Monthly Hours" value={`${analytics.monthly_hours || 0}h`} color="bg-purple-100 dark:bg-purple-900/30 text-purple-600" />
        <StatCard icon={HiOutlineClock} label="Avg Session" value={`${analytics.average_session_length || 0}h`} color="bg-green-100 dark:bg-green-900/30 text-green-600" />
        <StatCard icon={HiOutlineCheckCircle} label="Completion Rate" value={`${analytics.completion_rate || 0}%`} color="bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600" />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={HiOutlineAcademicCap} label="Most Studied" value={analytics.most_studied_topic || '—'} color="bg-orange-100 dark:bg-orange-900/30 text-orange-600" />
        <StatCard icon={HiOutlineSun} label="Fav Study Time" value={analytics.favorite_study_time || '—'} color="bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600" />
        <StatCard icon={HiOutlineFire} label="Current Streak" value={`${analytics.current_streak || 0} days`} color="bg-red-100 dark:bg-red-900/30 text-red-600" />
        <StatCard icon={HiOutlineTrophy} label="Longest Streak" value={`${analytics.longest_streak || 0} days`} color="bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Weekly Hours Bar Chart */}
        <div className="glass-card p-5">
          <h4 className="text-sm font-semibold mb-4">Weekly Hours (Last 8 Weeks)</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={analytics.weekly_hours_history || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="week" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="hours" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Status Distribution Pie Chart */}
        <div className="glass-card p-5">
          <h4 className="text-sm font-semibold mb-4">Session Status Distribution</h4>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-center py-8">No data</p>
          )}
        </div>
      </div>

      {/* Monthly Trend Line Chart */}
      <div className="glass-card p-5">
        <h4 className="text-sm font-semibold mb-4">Monthly Study Hours Trend</h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={analytics.monthly_hours_history || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="month" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Line type="monotone" dataKey="hours" stroke="#9333ea" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  )
}
