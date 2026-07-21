import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  HiOutlineLockClosed, HiOutlineEye, HiOutlineEyeSlash, HiOutlineCheckCircle,
} from 'react-icons/hi2'
import { resetPassword } from '../services/authApi'

function PasswordStrengthIndicator({ password }) {
  const getStrength = () => {
    let score = 0
    if (password.length >= 8) score++
    if (/[A-Z]/.test(password)) score++
    if (/[a-z]/.test(password)) score++
    if (/[0-9]/.test(password)) score++
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/.test(password)) score++
    return score
  }

  const strength = getStrength()
  const labels = ['', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong']
  const colors = ['', 'bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-emerald-500']

  if (!password) return null

  return (
    <div className="mt-2">
      <div className="flex gap-1 mb-1">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
              i <= strength ? colors[strength] : 'bg-gray-200 dark:bg-gray-700'
            }`}
          />
        ))}
      </div>
      <p className={`text-xs font-medium ${
        strength <= 2 ? 'text-red-500' : strength === 3 ? 'text-yellow-500' : 'text-green-500'
      }`}>
        {labels[strength]}
      </p>
    </div>
  )
}

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token') || ''

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [errors, setErrors] = useState({})

  const validate = () => {
    const errs = {}
    if (!newPassword) errs.newPassword = 'Password is required'
    else if (newPassword.length < 8) errs.newPassword = 'Password must be at least 8 characters'
    else {
      if (!/[A-Z]/.test(newPassword)) errs.newPassword = 'Password needs an uppercase letter'
      else if (!/[a-z]/.test(newPassword)) errs.newPassword = 'Password needs a lowercase letter'
      else if (!/[0-9]/.test(newPassword)) errs.newPassword = 'Password needs a number'
      else if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/.test(newPassword)) errs.newPassword = 'Password needs a special character'
    }
    if (newPassword !== confirmPassword) errs.confirmPassword = 'Passwords do not match'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    try {
      await resetPassword(token, newPassword, confirmPassword)
      setSuccess(true)
      toast.success('Password has been reset successfully!')
    } catch (err) {
      toast.error(err?.message || 'Failed to reset password. The token may be invalid or expired.')
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md text-center"
        >
          <div className="mb-8">
            <Link to="/" className="inline-flex items-center gap-2 mb-6">
              <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
                <span className="text-white font-bold">LM</span>
              </div>
              <span className="font-display font-bold text-2xl gradient-text">LearnMate</span>
            </Link>
            <h1 className="text-2xl font-bold mb-1">Invalid Reset Link</h1>
            <p className="text-gray-500 dark:text-gray-400">This password reset link is invalid or missing a token.</p>
          </div>
          <div className="glass-card p-6 sm:p-8">
            <Link to="/forgot-password" className="btn-primary w-full block text-center">
              Request a New Reset Link
            </Link>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md text-center"
      >
        <div className="mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
              <span className="text-white font-bold">LM</span>
            </div>
            <span className="font-display font-bold text-2xl gradient-text">LearnMate</span>
          </Link>
          <h1 className="text-2xl font-bold mb-1">Set new password</h1>
          <p className="text-gray-500 dark:text-gray-400">Choose a strong password for your account</p>
        </div>

        <div className="glass-card p-6 sm:p-8">
          {success ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-4"
            >
              <div className="flex justify-center mb-2">
                <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <HiOutlineCheckCircle className="w-6 h-6 text-green-600" />
                </div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Your password has been updated successfully.
              </p>
              <button
                onClick={() => navigate('/login')}
                className="btn-primary w-full"
              >
                Sign In with New Password
              </button>
            </motion.div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1.5 text-left">New Password</label>
                <div className="relative">
                  <HiOutlineLockClosed className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className={`input-field !pl-10 !pr-10 ${errors.newPassword ? 'ring-2 ring-red-500' : ''}`}
                    placeholder="Min 8 chars, uppercase, lowercase, number, special"
                    autoComplete="new-password"
                    autoFocus
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <HiOutlineEyeSlash className="w-4 h-4" /> : <HiOutlineEye className="w-4 h-4" />}
                  </button>
                </div>
                {errors.newPassword && <p className="text-red-500 text-xs mt-1">{errors.newPassword}</p>}
                <PasswordStrengthIndicator password={newPassword} />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1.5 text-left">Confirm Password</label>
                <div className="relative">
                  <HiOutlineLockClosed className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className={`input-field !pl-10 ${errors.confirmPassword ? 'ring-2 ring-red-500' : ''}`}
                    placeholder="Re-enter your password"
                    autoComplete="new-password"
                  />
                </div>
                {errors.confirmPassword && <p className="text-red-500 text-xs mt-1">{errors.confirmPassword}</p>}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Resetting password...
                  </>
                ) : (
                  'Reset Password'
                )}
              </button>
            </form>
          )}

          {!success && (
            <Link
              to="/login"
              className="mt-4 inline-block text-sm text-primary-600 dark:text-primary-400 hover:underline"
            >
              Back to Sign In
            </Link>
          )}
        </div>
      </motion.div>
    </div>
  )
}
