import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { HiOutlineUser } from 'react-icons/hi2'
import { useAuth } from '../context/AuthContext'
import { useGuest } from '../context/GuestContext'
import RegisterForm from '../components/auth/RegisterForm'

export default function Register() {
  const { register, isAuthenticated } = useAuth()
  const { enterGuestMode, exitGuestMode } = useGuest()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  if (isAuthenticated) {
    navigate('/dashboard', { replace: true })
    return null
  }

  const handleRegister = async (data) => {
    setLoading(true)
    try {
      await register(data)
      exitGuestMode()
      toast.success('Account created successfully! Please sign in.')
      navigate('/login', { replace: true })
    } catch (err) {
      toast.error(err?.message || 'Registration failed')
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
          <h1 className="text-2xl font-bold mb-1">Create your account</h1>
          <p className="text-gray-500 dark:text-gray-400">Start your personalized learning journey</p>
        </div>

        <div className="glass-card p-6 sm:p-8">
          <RegisterForm onSubmit={handleRegister} loading={loading} />
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
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-primary-600 dark:text-primary-400 hover:underline">
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  )
}
