import { useState, useEffect, useCallback } from 'react'
import { HiOutlineBell, HiOutlineBellSlash } from 'react-icons/hi2'

export default function ReminderSettings({ sessions }) {
  const [permission, setPermission] = useState(
    typeof Notification !== 'undefined' ? Notification.permission : 'default'
  )

  const requestPermission = useCallback(async () => {
    if (typeof Notification === 'undefined') return
    const result = await Notification.requestPermission()
    setPermission(result)
  }, [])

  useEffect(() => {
    if (permission !== 'granted' || !sessions?.length) return

    const interval = setInterval(() => {
      const now = new Date()
      sessions.forEach((s) => {
        if (s.status !== 'scheduled') return
        if (!s.reminder_minutes || s.reminder_minutes <= 0) return
        try {
          const sessionTime = new Date(`${s.date}T${s.start_time}:00`)
          const reminderTime = new Date(sessionTime.getTime() - s.reminder_minutes * 60000)
          const diff = Math.abs(now.getTime() - reminderTime.getTime())
          if (diff < 60000) {
            new Notification('Study Session Reminder', {
              body: `"${s.title}" starts in ${s.reminder_minutes} minutes`,
              icon: '/favicon.ico',
            })
          }
        } catch {}
      })
    }, 60000)

    return () => clearInterval(interval)
  }, [sessions, permission])

  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50">
      {permission === 'granted' ? (
        <HiOutlineBell className="w-5 h-5 text-green-500 shrink-0" />
      ) : (
        <HiOutlineBellSlash className="w-5 h-5 text-gray-400 shrink-0" />
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">Browser Notifications</p>
        <p className="text-xs text-gray-500">
          {permission === 'granted' ? 'Enabled — you\'ll receive reminders' : 'Enable to get session reminders'}
        </p>
      </div>
      {permission !== 'granted' && (
        <button onClick={requestPermission} className="btn-secondary text-xs px-3 py-1.5">
          Enable
        </button>
      )}
    </div>
  )
}
