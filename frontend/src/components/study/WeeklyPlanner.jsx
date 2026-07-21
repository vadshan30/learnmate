import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { HiOutlinePlus } from 'react-icons/hi2'
import StudySessionCard from './StudySessionCard'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const SHORT_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export default function WeeklyPlanner({ sessions, onComplete, onDelete, onEdit, onAddSession }) {
  const weeklyData = useMemo(() => {
    const now = new Date()
    const monday = new Date(now)
    monday.setDate(now.getDate() - now.getDay() + 1)
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)

    const mondayStr = monday.toISOString().split('T')[0]
    const sundayStr = sunday.toISOString().split('T')[0]

    const grouped = {}
    DAY_NAMES.forEach((day) => { grouped[day] = [] })

    ;(sessions || []).forEach((s) => {
      if (s.date >= mondayStr && s.date <= sundayStr) {
        const dt = new Date(s.date + 'T00:00:00')
        const dayIdx = (dt.getDay() + 6) % 7
        grouped[DAY_NAMES[dayIdx]].push(s)
      }
    })

    DAY_NAMES.forEach((day) => {
      grouped[day].sort((a, b) => (a.start_time || '').localeCompare(b.start_time || ''))
    })

    return grouped
  }, [sessions])

  const today = new Date()
  const todayName = DAY_NAMES[(today.getDay() + 6) % 7]

  return (
    <motion.div variants={fadeUp}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Weekly Planner</h3>
        <button onClick={onAddSession} className="btn-primary text-sm px-4 py-2 flex items-center gap-1.5">
          <HiOutlinePlus className="w-4 h-4" />
          Add Session
        </button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3">
        {DAY_NAMES.map((day, idx) => {
          const isToday = day === todayName
          const daySessions = weeklyData[day]
          return (
            <div
              key={day}
              className={`rounded-2xl border p-3 min-h-[200px] transition-all ${
                isToday
                  ? 'border-primary-300 dark:border-primary-700 bg-primary-50/50 dark:bg-primary-950/30'
                  : 'border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className={`text-sm font-semibold ${isToday ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-gray-400'}`}>
                  {SHORT_DAYS[idx]}
                </span>
                {isToday && (
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full gradient-bg text-white">
                    Today
                  </span>
                )}
              </div>
              <div className="space-y-2">
                {daySessions.length > 0 ? (
                  daySessions.map((session) => (
                    <StudySessionCard
                      key={session.id}
                      session={session}
                      onComplete={onComplete}
                      onDelete={onDelete}
                      onEdit={onEdit}
                    />
                  ))
                ) : (
                  <p className="text-xs text-gray-400 dark:text-gray-500 text-center py-4">
                    No Sessions
                  </p>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}
