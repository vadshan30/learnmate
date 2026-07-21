import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  HiOutlineUser, HiOutlineEnvelope, HiOutlineLockClosed,
  HiOutlineEye, HiOutlineEyeSlash,
} from 'react-icons/hi2'

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

export default function RegisterForm({ onSubmit, loading }) {
  const [fullName, setFullName] = useState('')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [errors, setErrors] = useState({})

  const validate = () => {
    const errs = {}
    if (!fullName.trim()) errs.fullName = 'Full name is required'
    if (!username.trim()) errs.username = 'Username is required'
    else if (username.trim().length < 3) errs.username = 'Username must be at least 3 characters'
    else if (!/^[a-zA-Z0-9_-]+$/.test(username.trim())) errs.username = 'Username can only contain letters, numbers, underscores, and hyphens'
    if (!email.trim()) errs.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) errs.email = 'Invalid email format'
    if (!password) errs.password = 'Password is required'
    else if (password.length < 8) errs.password = 'Password must be at least 8 characters'
    else {
      if (!/[A-Z]/.test(password)) errs.password = 'Password needs an uppercase letter'
      else if (!/[a-z]/.test(password)) errs.password = 'Password needs a lowercase letter'
      else if (!/[0-9]/.test(password)) errs.password = 'Password needs a number'
      else if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/.test(password)) errs.password = 'Password needs a special character'
    }
    if (password !== confirmPassword) errs.confirmPassword = 'Passwords do not match'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!validate()) return
    onSubmit({
      full_name: fullName.trim(),
      username: username.trim().toLowerCase(),
      email: email.trim().toLowerCase(),
      password,
      confirm_password: confirmPassword,
    })
  }

  const fields = [
    { label: 'Full Name', value: fullName, set: setFullName, type: 'text', icon: HiOutlineUser, placeholder: 'Alice Johnson', key: 'fullName', autoComplete: 'name' },
    { label: 'Username', value: username, set: setUsername, type: 'text', icon: HiOutlineUser, placeholder: 'alice', key: 'username', autoComplete: 'username' },
    { label: 'Email', value: email, set: setEmail, type: 'email', icon: HiOutlineEnvelope, placeholder: 'alice@example.com', key: 'email', autoComplete: 'email' },
  ]

  return (
    <motion.form
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit}
      className="space-y-4"
    >
      {fields.map((f) => (
        <div key={f.key}>
          <label className="block text-sm font-medium mb-1.5">{f.label}</label>
          <div className="relative">
            <f.icon className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type={f.type}
              value={f.value}
              onChange={(e) => f.set(e.target.value)}
              className={`input-field !pl-10 ${errors[f.key] ? 'ring-2 ring-red-500' : ''}`}
              placeholder={f.placeholder}
              autoComplete={f.autoComplete}
            />
          </div>
          {errors[f.key] && <p className="text-red-500 text-xs mt-1">{errors[f.key]}</p>}
        </div>
      ))}

      <div>
        <label className="block text-sm font-medium mb-1.5">Password</label>
        <div className="relative">
          <HiOutlineLockClosed className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={`input-field !pl-10 !pr-10 ${errors.password ? 'ring-2 ring-red-500' : ''}`}
            placeholder="Min 8 chars, uppercase, lowercase, number, special"
            autoComplete="new-password"
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
        <PasswordStrengthIndicator password={password} />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5">Confirm Password</label>
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
            Creating account...
          </>
        ) : (
          'Create Account'
        )}
      </button>
    </motion.form>
  )
}
