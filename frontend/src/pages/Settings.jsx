import { useState } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { HiOutlineTrash, HiOutlineSun, HiOutlineMoon, HiOutlineArrowPath } from 'react-icons/hi2'
import { useTheme } from '../context/ThemeContext'
import { useApp } from '../context/AppContext'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.08 } } }

export default function Settings() {
  const { dark, toggle } = useTheme()
  const { student, removeStudent, health } = useApp()
  const [confirming, setConfirming] = useState(false)

  const handleDelete = async () => {
    try {
      await removeStudent()
      toast.success('Profile deleted')
    } catch (e) {
      toast.error(e?.message || 'Failed to delete profile')
    }
    setConfirming(false)
  }

  return (
    <div className="page-container max-w-3xl">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        <motion.div variants={fadeUp}>
          <h1 className="text-2xl sm:text-3xl font-display font-bold mb-8">Settings</h1>
        </motion.div>

        {/* Appearance */}
        <motion.div variants={fadeUp} className="glass-card p-6 mb-6">
          <h2 className="font-semibold mb-4">Appearance</h2>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {dark ? <HiOutlineMoon className="w-5 h-5 text-primary-400" /> : <HiOutlineSun className="w-5 h-5 text-yellow-500" />}
              <div>
                <p className="font-medium">Dark Mode</p>
                <p className="text-sm text-gray-500">{dark ? 'Currently dark' : 'Currently light'}</p>
              </div>
            </div>
            <button onClick={toggle} className={`relative w-12 h-6 rounded-full transition-colors ${dark ? 'bg-primary-600' : 'bg-gray-300'}`}>
              <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform ${dark ? 'translate-x-6' : ''}`} />
            </button>
          </div>
        </motion.div>

        {/* Account */}
        <motion.div variants={fadeUp} className="glass-card p-6 mb-6">
          <h2 className="font-semibold mb-4">Account</h2>
          {student ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-xl">
                <div>
                  <p className="font-medium">{student.name}</p>
                  <p className="text-sm text-gray-500">{student.student_id}</p>
                </div>
              </div>
              {!confirming ? (
                <button onClick={() => setConfirming(true)} className="flex items-center gap-2 text-sm text-red-500 hover:text-red-600 font-medium">
                  <HiOutlineTrash className="w-4 h-4" /> Delete Profile
                </button>
              ) : (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800">
                  <p className="text-sm text-red-700 dark:text-red-400 mb-3">Are you sure? This will delete your profile, roadmap, and chat history.</p>
                  <div className="flex gap-2">
                    <button onClick={handleDelete} className="px-4 py-2 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700">Yes, Delete</button>
                    <button onClick={() => setConfirming(false)} className="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800">Cancel</button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No profile created yet.</p>
          )}
        </motion.div>

        {/* System */}
        <motion.div variants={fadeUp} className="glass-card p-6">
          <h2 className="font-semibold mb-4">System</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Backend Status</span>
              <span className={health?.status === 'ok' ? 'text-green-600 font-medium' : 'text-red-500 font-medium'}>
                {health?.status === 'ok' ? 'Connected' : 'Unavailable'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">RAG Service</span>
              <span className={health?.rag_available ? 'text-green-600' : 'text-yellow-600'}>
                {health?.services?.rag === 'healthy' ? 'Healthy' :
                 health?.services?.rag === 'empty' ? 'Empty (no data)' :
                 health?.services?.rag === 'error' ? 'Error' :
                 health?.rag_available ? 'Available' : 'Unavailable'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">WatsonX AI</span>
              <span className={health?.watsonx_available ? 'text-green-600' : 'text-yellow-600'}>
                {health?.watsonx_available ? 'Available' : 'Unavailable'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Version</span>
              <span>{health?.version || '1.0.0'}</span>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  )
}
