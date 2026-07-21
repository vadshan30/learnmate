import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { HiOutlineUser } from 'react-icons/hi2'
import { useAuth } from '../context/AuthContext'
import { useApp } from '../context/AppContext'
import { useGuest } from '../context/GuestContext'
import LoginForm from '../components/auth/LoginForm'

export default function Login() {
  const { login, isAuthenticated, accessToken } = useAuth()
  const { initStudentForUser } = useApp()
  const { enterGuestMode, isGuest, hasGuestData, getGuestDataForMigration, exitGuestMode } = useGuest()
  const navigate = useNavigate()
  const location = useLocation()
  const [loading, setLoading] = useState(false)

  const from = location.state?.from?.pathname || '/dashboard'

  if (isAuthenticated) {
    navigate(from, { replace: true })
    return null
  }

  const handleLogin = async (data, remember = true) => {
    setLoading(true)
    try {
      const result = await login(data, remember)
      await initStudentForUser(result.user.id, result.user.full_name)

      if (isGuest && hasGuestData()) {
        const guestPayload = getGuestDataForMigration()
        const hasContent = Object.keys(guestPayload).length > 0
        if (hasContent) {
          const confirmed = window.confirm(
            'We found Guest Mode progress on this device.\n\nWould you like to import your guest data into your account?'
          )
          if (confirmed) {
            try {
              const { migrateGuestData } = await import('../services/authApi')
              const token = localStorage.getItem('learnmate_access_token') || sessionStorage.getItem('learnmate_access_token')
              await migrateGuestData(guestPayload, token)
              toast.success('Guest progress imported successfully!')
              exitGuestMode()
            } catch {
              toast.error('Failed to import guest data. You can try again later.')
            }
          } else {
            exitGuestMode()
          }
        } else {
          exitGuestMode()
        }
      }

      toast.success('Welcome back!')
      navigate(from, { replace: true })
    } catch (err) {
      if (err?.status === 429) {
        toast.error(err?.message || 'Too many login attempts. Please wait 15 minutes.')
      } else {
        toast.error(err?.message || 'Invalid username or password')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleGuest = () => {
    enterGuestMode()
    toast.success('Welcome! You are in Guest Mode.')
    navigate('/dashboard', { replace: true })
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
              <span className="text-white font-bold">LM</span>
            </div>
            <span className="font-display font-bold text-2xl gradient-text">LearnMate</span>
          </Link>
          <h1 className="text-2xl font-bold mb-1">Welcome back</h1>
          <p className="text-gray-500 dark:text-gray-400">Sign in to continue your learning journey</p>
        </div>

        <div className="glass-card p-6 sm:p-8">
          <LoginForm onSubmit={handleLogin} loading={loading} />
        </div>

        <div className="mt-4">
          <button
            onClick={handleGuest}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all duration-200 active:scale-[0.98]"
          >
            <HiOutlineUser className="w-5 h-5" />
            Continue as Guest
          </button>
        </div>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="font-medium text-primary-600 dark:text-primary-400 hover:underline">
            Sign up
          </Link>
        </p>
      </motion.div>
    </div>
  )
}
