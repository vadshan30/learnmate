import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { HiOutlineXMark, HiOutlineClock, HiOutlineCalendarDays } from 'react-icons/hi2'

const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Low', color: 'text-green-600' },
  { value: 'medium', label: 'Medium', color: 'text-yellow-600' },
  { value: 'high', label: 'High', color: 'text-red-600' },
]

const DIFFICULTY_OPTIONS = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
]

const REMINDER_OPTIONS = [
  { value: 0, label: 'No reminder' },
  { value: 15, label: '15 minutes before' },
  { value: 30, label: '30 minutes before' },
  { value: 60, label: '1 hour before' },
  { value: 1440, label: '1 day before' },
]

const REPEAT_OPTIONS = [
  { value: 'none', label: 'None' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
]

export default function SessionModal({ open, onClose, onSave, session }) {
  const isEditing = !!session?.id

  const [form, setForm] = useState({
    title: '',
    description: '',
    topic: '',
    date: new Date().toISOString().split('T')[0],
    start_time: '18:00',
    end_time: '20:00',
    duration: 2.0,
    priority: 'medium',
    difficulty: 'medium',
    repeat_type: 'none',
    reminder_minutes: 15,
    course_id: '',
    project_id: '',
  })

  useEffect(() => {
    if (session) {
      setForm({
        title: session.title || '',
        description: session.description || '',
        topic: session.topic || '',
        date: session.date || new Date().toISOString().split('T')[0],
        start_time: session.start_time || '18:00',
        end_time: session.end_time || '20:00',
        duration: session.duration || 2.0,
        priority: session.priority || 'medium',
        difficulty: session.difficulty || 'medium',
        repeat_type: session.repeat_type || 'none',
        reminder_minutes: session.reminder_minutes ?? 15,
        course_id: session.course_id || '',
        project_id: session.project_id || '',
      })
    } else {
      setForm({
        title: '',
        description: '',
        topic: '',
        date: new Date().toISOString().split('T')[0],
        start_time: '18:00',
        end_time: '20:00',
        duration: 2.0,
        priority: 'medium',
        difficulty: 'medium',
        repeat_type: 'none',
        reminder_minutes: 15,
        course_id: '',
        project_id: '',
      })
    }
  }, [session, open])

  useEffect(() => {
    if (form.start_time && form.end_time) {
      try {
        const [sh, sm] = form.start_time.split(':').map(Number)
        const [eh, em] = form.end_time.split(':').map(Number)
        const dur = ((eh * 60 + em) - (sh * 60 + sm)) / 60
        if (dur > 0) setForm((p) => ({ ...p, duration: Math.round(dur * 100) / 100 }))
      } catch {}
    }
  }, [form.start_time, form.end_time])

  const handleChange = (field) => (e) => {
    setForm((p) => ({ ...p, [field]: e.target.value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.title.trim()) return
    const payload = {
      ...form,
      title: form.title.trim(),
      description: form.description.trim(),
      topic: form.topic.trim() || null,
      duration: Number(form.duration) || 2.0,
      reminder_minutes: Number(form.reminder_minutes),
      course_id: form.course_id.trim() || null,
      project_id: form.project_id.trim() || null,
    }
    onSave?.(payload)
  }

  if (!open) return null

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-4 sm:inset-auto sm:left-1/2 sm:top-1/2 sm:-translate-x-1/2 sm:-translate-y-1/2 sm:w-full sm:max-w-lg sm:max-h-[90vh] bg-white dark:bg-gray-900 rounded-2xl shadow-2xl z-50 overflow-y-auto"
          >
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800">
              <h2 className="text-xl font-bold">{isEditing ? 'Edit Session' : 'New Study Session'}</h2>
              <button onClick={onClose} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                <HiOutlineXMark className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Title *</label>
                <input
                  type="text"
                  value={form.title}
                  onChange={handleChange('title')}
                  className="input-field"
                  placeholder="e.g. Python Functions"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Topic</label>
                <input
                  type="text"
                  value={form.topic}
                  onChange={handleChange('topic')}
                  className="input-field"
                  placeholder="e.g. Python Basics"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={form.description}
                  onChange={handleChange('description')}
                  className="input-field resize-none"
                  rows={2}
                  placeholder="Optional notes..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    <HiOutlineCalendarDays className="w-4 h-4 inline mr-1" />
                    Date
                  </label>
                  <input
                    type="date"
                    value={form.date}
                    onChange={handleChange('date')}
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    <HiOutlineClock className="w-4 h-4 inline mr-1" />
                    Duration
                  </label>
                  <input
                    type="text"
                    value={`${form.duration}h`}
                    className="input-field bg-gray-50 dark:bg-gray-800"
                    readOnly
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Start Time</label>
                  <input
                    type="time"
                    value={form.start_time}
                    onChange={handleChange('start_time')}
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">End Time</label>
                  <input
                    type="time"
                    value={form.end_time}
                    onChange={handleChange('end_time')}
                    className="input-field"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Priority</label>
                  <select value={form.priority} onChange={handleChange('priority')} className="input-field">
                    {PRIORITY_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Difficulty</label>
                  <select value={form.difficulty} onChange={handleChange('difficulty')} className="input-field">
                    {DIFFICULTY_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Reminder</label>
                  <select value={form.reminder_minutes} onChange={handleChange('reminder_minutes')} className="input-field">
                    {REMINDER_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Repeat</label>
                  <select value={form.repeat_type} onChange={handleChange('repeat_type')} className="input-field">
                    {REPEAT_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button type="submit" className="btn-primary flex-1">
                  {isEditing ? 'Update Session' : 'Create Session'}
                </button>
                <button type="button" onClick={onClose} className="btn-ghost">
                  Cancel
                </button>
              </div>
            </form>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
