import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { HiOutlineEnvelope, HiOutlineCheckCircle } from 'react-icons/hi2'
import { forgotPassword } from '../services/authApi'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [resetLink, setResetLink] = useState('')
  const [errors, setErrors] = useState({})

  const validate = () => {
    const errs = {}
    if (!email.trim()) errs.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) errs.email = 'Invalid email format'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    try {
      const res = await forgotPassword(email.trim().toLowerCase())
      setSubmitted(true)
      const msg = res.data?.message || ''
      const linkMatch = msg.match(/\[DEV MODE\] Reset link:\s*(https?:\/\/[^\s]+)/)
      if (linkMatch) {
        setResetLink(linkMatch[1])
      }
      toast.success('If the account exists, a reset link has been sent.')
    } catch (err) {
      toast.error(err?.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
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
          <h1 className="text-2xl font-bold mb-1">Reset your password</h1>
          <p className="text-gray-500 dark:text-gray-400">
            {submitted
              ? 'Check your email for further instructions'
              : 'Enter your email and we will send you a reset link'}
          </p>
        </div>

        <div className="glass-card p-6 sm:p-8">
          {submitted ? (
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
                If an account exists with <strong>{email}</strong>, you will receive a password reset link shortly.
              </p>

              {resetLink && (
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <p className="text-xs text-blue-700 dark:text-blue-300 font-medium mb-1">Dev Mode - Reset Link:</p>
                  <a
                    href={resetLink}
                    className="text-xs text-blue-600 dark:text-blue-400 break-all underline hover:no-underline"
                  >
                    {resetLink}
                  </a>
                </div>
              )}

              <p className="text-xs text-gray-500 dark:text-gray-500">
                Didn't receive the email? Check your spam folder or try again.
              </p>
              <Link
                to="/login"
                className="btn-primary w-full block text-center"
              >
                Back to Sign In
              </Link>
            </motion.div>
          ) : (
            <>
              <div className="flex justify-center mb-4">
                <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                  <HiOutlineEnvelope className="w-6 h-6 text-primary-600" />
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5 text-left">Email address</label>
                  <div className="relative">
                    <HiOutlineEnvelope className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className={`input-field !pl-10 ${errors.email ? 'ring-2 ring-red-500' : ''}`}
                      placeholder="alice@example.com"
                      autoComplete="email"
                      autoFocus
                    />
                  </div>
                  {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Sending reset link...
                    </>
                  ) : (
                    'Send Reset Link'
                  )}
                </button>
              </form>
            </>
          )}

          {!submitted && (
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
