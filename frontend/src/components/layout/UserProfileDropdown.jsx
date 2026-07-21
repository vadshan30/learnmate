import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  HiOutlineUser,
  HiOutlineMap,
  HiOutlineChartBar,
  HiOutlineCog6Tooth,
  HiOutlineArrowRightOnRectangle,
  HiOutlineChevronRight,
  HiOutlineUserPlus,
} from 'react-icons/hi2'
import { useAuth } from '../../context/AuthContext'
import { useApp } from '../../context/AppContext'
import { useGuest } from '../../context/GuestContext'

const menuItems = [
  { to: '/profile', label: 'Profile', icon: HiOutlineUser },
  { to: '/roadmap', label: 'My Roadmap', icon: HiOutlineMap },
  { to: '/progress', label: 'My Progress', icon: HiOutlineChartBar },
  { to: '/settings', label: 'Settings', icon: HiOutlineCog6Tooth },
]

const dropdownVariants = {
  hidden: { opacity: 0, y: -8, scale: 0.95 },
  visible: { opacity: 1, y: 0, scale: 1 },
  exit: { opacity: 0, y: -8, scale: 0.95 },
}

export default function UserProfileDropdown() {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)
  const { user, logout } = useAuth()
  const { student, clearStudentData } = useApp()
  const { isGuest, exitGuestMode } = useGuest()
  const navigate = useNavigate()
  const [showGuestDialog, setShowGuestDialog] = useState(false)

  const displayName = (user?.full_name || student?.name || 'User').trim()
  const displayEmail = user?.email || ''
  const initials = displayName.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase()

  // Close on outside click
  useEffect(() => {
    if (!open) return
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  // Close on Escape key
  useEffect(() => {
    if (!open) return
    const handler = (e) => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [open])

  const handleLogout = () => {
    setOpen(false)
    if (isGuest) exitGuestMode()
    logout()
    clearStudentData()
    navigate('/login', { replace: true })
  }

  const handleMenuClick = () => setOpen(false)

  return (
    <div ref={ref} className="relative">
      {/* Trigger */}
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        aria-label="User menu"
        aria-expanded={open}
      >
        <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center shadow-sm">
          <span className="text-white text-sm font-semibold">{initials}</span>
        </div>
        <span className="hidden sm:block text-sm font-medium truncate max-w-[120px]">{displayName}</span>
      </button>

      {/* Dropdown */}
      <AnimatePresence>
        {open && (
          <motion.div
            variants={dropdownVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="absolute right-0 mt-2 w-72 bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 overflow-hidden z-50"
          >
            {/* User info header */}
            <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full gradient-bg flex items-center justify-center shadow-sm">
                  <span className="text-white font-semibold">{initials}</span>
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold truncate">{displayName}</p>
                  {displayEmail && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{displayEmail}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Menu items */}
            <div className="py-2">
              {menuItems.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={handleMenuClick}
                  className="flex items-center gap-3 px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group"
                >
                  <item.icon className="w-5 h-5 text-gray-400 dark:text-gray-500 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors" />
                  <span className="flex-1">{item.label}</span>
                  <HiOutlineChevronRight className="w-4 h-4 text-gray-300 dark:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                </Link>
              ))}

              {isGuest && (
                <>
                  <div className="my-2 border-t border-gray-100 dark:border-gray-800" />
                  <button
                    onClick={() => { setOpen(false); setShowGuestDialog(true) }}
                    className="flex items-center gap-3 w-full px-5 py-2.5 text-sm font-medium text-amber-600 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950/30 transition-colors"
                  >
                    <HiOutlineUserPlus className="w-5 h-5" />
                    <span>Create Account</span>
                  </button>
                </>
              )}

              {/* Divider before logout */}
              <div className="my-2 border-t border-gray-100 dark:border-gray-800" />

              {/* Logout */}
              <button
                onClick={handleLogout}
                className="flex items-center gap-3 w-full px-5 py-2.5 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
              >
                <HiOutlineArrowRightOnRectangle className="w-5 h-5" />
                <span>Logout</span>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showGuestDialog && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-[100]"
              onClick={() => setShowGuestDialog(false)}
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
                    onClick={() => setShowGuestDialog(false)}
                    className="px-4 py-2 text-sm font-medium rounded-lg border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  >
                    Continue as Guest
                  </button>
                  <button
                    onClick={() => { setShowGuestDialog(false); navigate('/register') }}
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
    </div>
  )
}
