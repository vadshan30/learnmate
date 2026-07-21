import { useState } from 'react'
import { motion } from 'framer-motion'
import { HiOutlineFire, HiOutlinePencil } from 'react-icons/hi2'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const PRESET_HOURS = [5, 10, 15, 20, 25]

export default function StudyGoalCard({ goal, onSave }) {
  const [editing, setEditing] = useState(false)
  const [hours, setHours] = useState(goal?.weekly_goal_hours || 10)
  const [customMode, setCustomMode] = useState(false)

  const currentHours = goal?.weekly_goal_hours || 10
  const completedHours = goal?.completed_hours || 0
  const progress = currentHours > 0 ? Math.min((completedHours / currentHours) * 100, 100) : 0

  const handleSave = () => {
    onSave?.({ weekly_goal_hours: hours })
    setEditing(false)
  }

  return (
    <motion.div variants={fadeUp} className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <HiOutlineFire className="w-5 h-5 text-orange-500" />
          Weekly Study Goal
        </h3>
        <button
          onClick={() => setEditing(!editing)}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <HiOutlinePencil className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {editing ? (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {PRESET_HOURS.map((h) => (
              <button
                key={h}
                onClick={() => { setHours(h); setCustomMode(false) }}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  hours === h && !customMode
                    ? 'gradient-bg text-white shadow-md'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                {h} Hours
              </button>
            ))}
            <button
              onClick={() => setCustomMode(true)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                customMode
                  ? 'gradient-bg text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
              }`}
            >
              Custom
            </button>
          </div>
          {customMode && (
            <div className="flex items-center gap-3">
              <input
                type="number"
                min="1"
                max="60"
                value={hours}
                onChange={(e) => setHours(Number(e.target.value))}
                className="input-field w-24"
              />
              <span className="text-sm text-gray-500">hours per week</span>
            </div>
          )}
          <div className="flex gap-2">
            <button onClick={handleSave} className="btn-primary text-sm px-4 py-2">Save</button>
            <button onClick={() => setEditing(false)} className="btn-ghost text-sm">Cancel</button>
          </div>
        </div>
      ) : (
        <>
          <div className="flex items-end gap-2 mb-3">
            <span className="text-3xl font-bold">{completedHours}</span>
            <span className="text-gray-400 mb-1">/ {currentHours} Hours</span>
          </div>
          <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full gradient-bg rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            />
          </div>
          <p className="text-sm text-gray-500 mt-2">{Math.round(progress)}% completed</p>
        </>
      )}
    </motion.div>
  )
}
