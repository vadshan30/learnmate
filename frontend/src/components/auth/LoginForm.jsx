import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { HiOutlineEnvelope, HiOutlineLockClosed, HiOutlineEye, HiOutlineEyeSlash } from 'react-icons/hi2'

export default function LoginForm({ onSubmit, loading }) {
  const [emailOrUsername, setEmailOrUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(true)
  const [errors, setErrors] = useState({})

  const validate = () => {
    const errs = {}
    if (!emailOrUsername.trim()) errs.emailOrUsername = 'Email or username is required'
    if (!password) errs.password = 'Password is required'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!validate()) return
    onSubmit({ email_or_username: emailOrUsername.trim(), password }, rememberMe)
  }

  return (
    <motion.form
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit}
      className="space-y-5"
    >
      <div>
        <label className="block text-sm font-medium mb-1.5">Email or Username</label>
        <div className="relative">
          <HiOutlineEnvelope className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={emailOrUsername}
            onChange={(e) => setEmailOrUsername(e.target.value)}
            className={`input-field !pl-10 ${errors.emailOrUsername ? 'ring-2 ring-red-500' : ''}`}
            placeholder="alice@example.com or alice"
            autoComplete="username"
          />
        </div>
        {errors.emailOrUsername && <p className="text-red-500 text-xs mt-1">{errors.emailOrUsername}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5">Password</label>
        <div className="relative">
          <HiOutlineLockClosed className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={`input-field !pl-10 !pr-10 ${errors.password ? 'ring-2 ring-red-500' : ''}`}
            placeholder="Enter your password"
            autoComplete="current-password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            {showPassword ? <HiOutlineEyeSlash className="w-4 h-4" /> : <HiOutlineEye className="w-4 h-4" />}
          </button>
        </div>
        {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
      </div>

      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 cursor-pointer">
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            className="rounded border-gray-300 accent-primary-600"
          />
          Remember me
        </label>
        <Link to="/forgot-password" className="text-sm text-primary-600 dark:text-primary-400 hover:underline">
          Forgot password?
        </Link>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="btn-primary w-full flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Signing in...
          </>
        ) : (
          'Sign In'
        )}
      </button>
    </motion.form>
  )
}
