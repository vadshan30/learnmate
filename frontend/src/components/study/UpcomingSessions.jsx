import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { HiOutlineClock, HiOutlinePlay, HiOutlineArrowRight } from 'react-icons/hi2'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

function Countdown({ targetDate }) {
  const [timeLeft, setTimeLeft] = useState('')

  useEffect(() => {
    const calc = () => {
      const now = new Date()
      const target = new Date(targetDate)
      const diff = target - now
      if (diff <= 0) { setTimeLeft('Now'); return }
      const hours = Math.floor(diff / 3600000)
      const mins = Math.floor((diff % 3600000) / 60000)
      const secs = Math.floor((diff % 60000) / 1000)
      setTimeLeft(`${hours}h ${mins}m ${secs}s`)
    }
    calc()
    const timer = setInterval(calc, 1000)
    return () => clearInterval(timer)
  }, [targetDate])

  return <span className="font-mono text-sm font-bold text-primary-600 dark:text-primary-400">{timeLeft}</span>
}

export default function UpcomingSessions({ sessions, onStartSession }) {
  const upcoming = (sessions || [])
    .filter((s) => s.status === 'scheduled' || s.status === 'in_progress')
    .sort((a, b) => {
      const da = `${a.date}T${a.start_time || '00:00'}`
      const db = `${b.date}T${b.start_time || '00:00'}`
      return da.localeCompare(db)
    })
    .slice(0, 5)

  const nextSession = upcoming[0]
  const nextDate = nextSession ? `${nextSession.date}T${nextSession.start_time || '18:00'}:00` : null

  return (
    <motion.div variants={fadeUp} className="glass-card p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <HiOutlineClock className="w-5 h-5 text-primary-500" />
        Upcoming Sessions
      </h3>

      {nextSession && (
        <div className="bg-primary-50 dark:bg-primary-950/30 rounded-xl p-4 mb-4">
          <p className="text-xs text-gray-500 mb-1">Next Session In</p>
          <Countdown targetDate={nextDate} />
          <p className="text-sm font-medium mt-1">{nextSession.title}</p>
          <p className="text-xs text-gray-500">{nextSession.date} at {nextSession.start_time}</p>
          <button
            onClick={() => onStartSession?.(nextSession)}
            className="mt-3 flex items-center gap-1.5 text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            <HiOutlinePlay className="w-4 h-4" />
            Quick Start
          </button>
        </div>
      )}

      <div className="space-y-2">
        {upcoming.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">No upcoming sessions</p>
        ) : (
          upcoming.map((s) => (
            <div key={s.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{s.title}</p>
                <p className="text-xs text-gray-500">{s.date} · {s.start_time} · {s.duration}h</p>
              </div>
              <HiOutlineArrowRight className="w-4 h-4 text-gray-400 shrink-0" />
            </div>
          ))
        )}
      </div>
    </motion.div>
  )
}
