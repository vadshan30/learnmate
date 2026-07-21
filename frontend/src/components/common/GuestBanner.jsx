import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { HiOutlineUserPlus } from 'react-icons/hi2'
import { useGuest } from '../../context/GuestContext'

export default function GuestBanner() {
  const { isGuest } = useGuest()
  const navigate = useNavigate()
  const [showDialog, setShowDialog] = useState(false)

  const handleCreateAccount = () => {
    setShowDialog(true)
  }

  const handleConfirm = () => {
    setShowDialog(false)
    navigate('/register')
  }

  const handleDismiss = () => {
    setShowDialog(false)
  }

  return (
    <>
      <AnimatePresence>
        {isGuest && (
          <motion.div
            initial={{ opacity: 0, y: -20, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: -20, height: 0 }}
            className="overflow-hidden"
          >
            <div className="bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800/50 px-4 py-3">
              <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
                <p className="text-sm text-amber-800 dark:text-amber-200">
                  <strong>Guest Mode</strong> — Your data is saved locally.{' '}
                  <button
                    onClick={handleCreateAccount}
                    className="font-semibold underline hover:text-amber-600 dark:hover:text-amber-100 cursor-pointer bg-transparent border-none p-0 text-inherit"
                  >
                    Create an account
                  </button>{' '}
                  to permanently save your progress.
                </p>
                <button
                  onClick={handleCreateAccount}
                  className="shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-600 text-white text-sm font-medium hover:bg-amber-700 transition-colors"
                >
                  <HiOutlineUserPlus className="w-4 h-4" />
                  Sign Up
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showDialog && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-[100]"
              onClick={handleDismiss}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              className="fixed inset-0 z-[101] flex items-center justify-center p-4"
            >
              <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-800 max-w-md w-full p-6">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                  Create an account
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                  Create an account to permanently save your learning progress.
                </p>
                <div className="flex gap-3 justify-end">
                  <button
                    onClick={handleDismiss}
                    className="px-4 py-2 text-sm font-medium rounded-lg border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  >
                    Continue as Guest
                  </button>
                  <button
                    onClick={handleConfirm}
                    className="px-4 py-2 text-sm font-medium rounded-lg bg-primary-600 text-white hover:bg-primary-700 transition-colors"
                  >
                    Create Account
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
