import { motion } from 'framer-motion'
import {
  HiOutlineClock, HiOutlineFire, HiOutlineCheckCircle, HiOutlineCalendarDays,
} from 'react-icons/hi2'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

export default function StudyPlannerDashboard({ dashboard }) {
  if (!dashboard) return null

  const cards = [
    {
      icon: HiOutlineCalendarDays,
      label: 'Planned Hours This Week',
      value: `${dashboard.planned_hours_this_week || 0} Hours`,
      color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600',
    },
    {
      icon: HiOutlineClock,
      label: 'Weekly Goal',
      value: `${dashboard.weekly_goal_hours || 0} Hours`,
      sub: `${dashboard.weekly_goal_progress || 0}%`,
      color: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600',
    },
    {
      icon: HiOutlineFire,
      label: 'Current Study Streak',
      value: `${dashboard.current_streak || 0} Days`,
      color: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600',
    },
    {
      icon: HiOutlineCheckCircle,
      label: 'Sessions Completed',
      value: `${dashboard.sessions_completed || 0} / ${dashboard.sessions_total || 0}`,
      color: 'bg-green-100 dark:bg-green-900/30 text-green-600',
    },
  ]

  return (
    <motion.div variants={fadeUp} className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {cards.map((card, i) => (
        <motion.div
          key={i}
          variants={fadeUp}
          whileHover={{ y: -2 }}
          className="glass-card p-5 flex items-center gap-4"
        >
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${card.color}`}>
            <card.icon className="w-6 h-6" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-gray-500 dark:text-gray-400">{card.label}</p>
            <p className="text-xl font-bold truncate">{card.value}</p>
            {card.sub && (
              <p className="text-xs text-gray-400">{card.sub}</p>
            )}
          </div>
        </motion.div>
      ))}
    </motion.div>
  )
}
