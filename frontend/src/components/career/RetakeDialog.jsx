import { motion, AnimatePresence } from 'framer-motion'
import { HiOutlineExclamationTriangle, HiOutlineArrowPath, HiOutlineXMark } from 'react-icons/hi2'

export default function RetakeDialog({ open, onClose, onConfirm, previousCareer, previousScore }) {
  if (!open) return null

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            className="fixed z-50 w-full max-w-md glass-card p-6 shadow-2xl"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                  <HiOutlineExclamationTriangle className="w-5 h-5 text-amber-600" />
                </div>
                <h3 className="text-lg font-semibold">Retake Career Test?</h3>
              </div>
              <button onClick={onClose} className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                <HiOutlineXMark className="w-5 h-5" />
              </button>
            </div>

            <div className="mb-6 space-y-3">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                You are about to retake the career aptitude test. Your previous results will be saved in history.
              </p>
              {previousCareer && (
                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Previous Result</p>
                  <p className="text-sm font-semibold">{previousCareer} — {Math.round(previousScore || 0)}%</p>
                </div>
              )}
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Your new result will become the active career match used across LearnMate AI.
              </p>
            </div>

            <div className="flex gap-3">
              <button onClick={onClose} className="btn-secondary flex-1">
                Cancel
              </button>
              <button onClick={onConfirm} className="btn-primary flex-1 flex items-center justify-center gap-2">
                <HiOutlineArrowPath className="w-4 h-4" /> Retake Test
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
