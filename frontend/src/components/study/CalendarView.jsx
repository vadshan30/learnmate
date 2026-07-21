import { useState, useMemo, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Calendar, dateFnsLocalizer, Views } from 'react-big-calendar'
import { format, parse, startOfWeek, getDay, addDays, startOfMonth, endOfMonth } from 'date-fns'
import 'react-big-calendar/lib/css/react-big-calendar.css'
import { HiOutlineCalendarDays, HiOutlineViewColumns, HiOutlineListBullet } from 'react-icons/hi2'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

const locales = { 'en-US': format }
const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
  getDay,
  locales,
})

const STATUS_COLORS = {
  scheduled: { backgroundColor: '#3b82f6', borderColor: '#2563eb' },
  in_progress: { backgroundColor: '#eab308', borderColor: '#ca8a04' },
  completed: { backgroundColor: '#22c55e', borderColor: '#16a34a' },
  skipped: { backgroundColor: '#a855f7', borderColor: '#9333ea' },
  missed: { backgroundColor: '#ef4444', borderColor: '#dc2626' },
}

const VIEWS = [
  { key: Views.MONTH, label: 'Month', icon: HiOutlineCalendarDays },
  { key: Views.WEEK, label: 'Week', icon: HiOutlineViewColumns },
  { key: Views.AGENDA, label: 'Agenda', icon: HiOutlineListBullet },
]

export default function CalendarView({ sessions, onEventClick }) {
  const [currentView, setCurrentView] = useState(Views.MONTH)
  const [currentDate, setCurrentDate] = useState(new Date())

  const events = useMemo(() => {
    return (sessions || []).map((s) => {
      const [sh, sm] = (s.start_time || '18:00').split(':').map(Number)
      const [eh, em] = (s.end_time || '20:00').split(':').map(Number)
      const baseDate = new Date(s.date + 'T00:00:00')
      const start = new Date(baseDate)
      start.setHours(sh || 18, sm || 0, 0, 0)
      const end = new Date(baseDate)
      end.setHours(eh || 20, em || 0, 0, 0)

      return {
        id: s.id,
        title: s.title || 'Study Session',
        start,
        end,
        status: s.status,
        priority: s.priority,
        topic: s.topic,
        resource: s,
      }
    })
  }, [sessions])

  const eventStyleGetter = useCallback((event) => {
    const colors = STATUS_COLORS[event.status] || STATUS_COLORS.scheduled
    return {
      style: {
        backgroundColor: colors.backgroundColor,
        borderRadius: '8px',
        opacity: 0.9,
        color: 'white',
        border: 'none',
        fontSize: '12px',
        padding: '2px 6px',
      },
    }
  }, [])

  const handleSelectEvent = useCallback((event) => {
    onEventClick?.(event.resource)
  }, [onEventClick])

  return (
    <motion.div variants={fadeUp} className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <HiOutlineCalendarDays className="w-5 h-5 text-primary-500" />
          Calendar
        </h3>
        <div className="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
          {VIEWS.map((v) => (
            <button
              key={v.key}
              onClick={() => setCurrentView(v.key)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                currentView === v.key
                  ? 'bg-white dark:bg-gray-700 shadow-sm text-primary-600 dark:text-primary-400'
                  : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              <v.icon className="w-3.5 h-3.5" />
              {v.label}
            </button>
          ))}
        </div>
      </div>
      <div style={{ height: currentView === Views.MONTH ? 600 : 400 }}>
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          view={currentView}
          date={currentDate}
          onView={(view) => setCurrentView(view)}
          onNavigate={(date) => setCurrentDate(date)}
          onSelectEvent={handleSelectEvent}
          eventPropGetter={eventStyleGetter}
          toolbar={false}
          style={{ fontFamily: 'Inter, sans-serif' }}
        />
      </div>
    </motion.div>
  )
}
