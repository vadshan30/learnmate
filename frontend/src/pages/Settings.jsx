import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  HiOutlineTrash, HiOutlineSun, HiOutlineMoon,
  HiOutlineKey, HiOutlineArrowPath, HiOutlineBell, HiOutlineEnvelope,
  HiOutlineAcademicCap, HiOutlineClock, HiOutlineUser, HiOutlineCheckCircle,
  HiOutlineExclamationTriangle, HiOutlineXCircle, HiOutlineGlobeAlt,
  HiOutlineShieldCheck, HiOutlineCog6Tooth, HiOutlineArrowRight,
  HiOutlineEye, HiOutlineEyeSlash, HiOutlineInformationCircle,
  HiOutlineCodeBracket, HiOutlineDocumentDuplicate, HiOutlineChevronDown,
  HiOutlineChevronRight, HiOutlineServer, HiOutlineCpuChip
} from 'react-icons/hi2'
import { useTheme } from '../context/ThemeContext'
import { useApp } from '../context/AppContext'
import { useAuth } from '../context/AuthContext'
import * as authApi from '../services/authApi'
import { getHealth } from '../services/api'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.08 } } }

const LEARNING_STYLES = [
  { value: 'video', label: 'Video' },
  { value: 'reading', label: 'Reading' },
  { value: 'hands-on', label: 'Hands-on' },
  { value: 'mixed', label: 'Mixed' },
]

const WEEKLY_GOALS = [
  { value: 5, label: '5 hrs/week' },
  { value: 10, label: '10 hrs/week' },
  { value: 15, label: '15 hrs/week' },
  { value: 20, label: '20 hrs/week' },
  { value: 30, label: '30+ hrs/week' },
]

function StatusBadge({ status }) {
  const config = {
    online: { dot: 'bg-green-500', bg: 'bg-green-100 dark:bg-green-900/40', text: 'text-green-700 dark:text-green-300', label: 'Online' },
    connected: { dot: 'bg-green-500', bg: 'bg-green-100 dark:bg-green-900/40', text: 'text-green-700 dark:text-green-300', label: 'Connected' },
    healthy: { dot: 'bg-green-500', bg: 'bg-green-100 dark:bg-green-900/40', text: 'text-green-700 dark:text-green-300', label: 'Running' },
    offline: { dot: 'bg-red-500', bg: 'bg-red-100 dark:bg-red-900/40', text: 'text-red-700 dark:text-red-300', label: 'Offline' },
    error: { dot: 'bg-red-500', bg: 'bg-red-100 dark:bg-red-900/40', text: 'text-red-700 dark:text-red-300', label: 'Error' },
    disabled: { dot: 'bg-gray-400', bg: 'bg-gray-100 dark:bg-gray-800', text: 'text-gray-600 dark:text-gray-400', label: 'Disabled' },
    empty: { dot: 'bg-yellow-500', bg: 'bg-yellow-100 dark:bg-yellow-900/40', text: 'text-yellow-700 dark:text-yellow-300', label: 'Empty' },
  }
  const normalized = status === 'healthy' ? 'healthy' : status === 'empty' ? 'empty' : status
  const c = config[normalized] || config.disabled
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${c.bg} ${c.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {c.label}
    </span>
  )
}

function Toggle({ enabled, onChange, disabled = false }) {
  return (
    <button
      onClick={() => !disabled && onChange(!enabled)}
      className={`relative w-11 h-6 rounded-full transition-colors flex-shrink-0 ${
        enabled ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform shadow-sm ${
        enabled ? 'translate-x-5' : ''
      }`} />
    </button>
  )
}

function SettingRow({ icon: Icon, iconColor, label, description, children }) {
  return (
    <div className="flex items-center justify-between py-3">
      <div className="flex items-center gap-3 min-w-0">
        <div className={`p-2 rounded-lg ${iconColor}`}>
          <Icon className="w-4 h-4" />
        </div>
        <div className="min-w-0">
          <p className="font-medium text-sm">{label}</p>
          {description && <p className="text-xs text-gray-500 dark:text-gray-400">{description}</p>}
        </div>
      </div>
      <div className="flex-shrink-0 ml-4">{children}</div>
    </div>
  )
}

function DiagnosticsRow({ label, value, mono = false }) {
  return (
    <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
      <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
      <span className={`text-sm font-medium ${mono ? 'font-mono text-xs' : ''}`}>{value}</span>
    </div>
  )
}

function formatUptime(seconds) {
  if (!seconds && seconds !== 0) return 'Unknown'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

function formatDbSize(kb) {
  if (kb === null || kb === undefined) return null
  if (kb >= 1024) return `${(kb / 1024).toFixed(1)} MB`
  return `${kb} KB`
}

export default function Settings() {
  const { dark, toggle: toggleTheme } = useTheme()
  const { student, removeStudent, health, saveStudent } = useApp()
  const { user, accessToken } = useAuth()

  const [confirming, setConfirming] = useState(false)
  const [showChangePassword, setShowChangePassword] = useState(false)
  const [passwordForm, setPasswordForm] = useState({ current_password: '', new_password: '', confirm_password: '' })
  const [showPasswords, setShowPasswords] = useState({ current: false, new: false, confirm: false })
  const [changingPassword, setChangingPassword] = useState(false)

  const [learningStyle, setLearningStyle] = useState(student?.learning_style || 'mixed')
  const [weeklyGoal, setWeeklyGoal] = useState(student?.hours_per_week || 10)
  const [aiRecommendations, setAiRecommendations] = useState(() => {
    return localStorage.getItem('learnmate_ai_recommendations') !== 'false'
  })
  const [studyReminders, setStudyReminders] = useState(() => {
    return localStorage.getItem('learnmate_study_reminders') !== 'false'
  })

  const [browserNotifications, setBrowserNotifications] = useState(() => {
    return localStorage.getItem('learnmate_browser_notifications') === 'true'
  })
  const [emailNotifications, setEmailNotifications] = useState(() => {
    return localStorage.getItem('learnmate_email_notifications') === 'true'
  })
  const [reminderNotifications, setReminderNotifications] = useState(() => {
    return localStorage.getItem('learnmate_reminder_notifications') !== 'false'
  })

  const [developerMode, setDeveloperMode] = useState(false)
  const [devHealth, setDevHealth] = useState(null)
  const [healthLoading, setHealthLoading] = useState(false)

  useEffect(() => {
    if (student) {
      setLearningStyle(student.learning_style || 'mixed')
      setWeeklyGoal(student.hours_per_week || 10)
    }
  }, [student])

  const refreshHealth = useCallback(async () => {
    setHealthLoading(true)
    try {
      const r = await getHealth()
      setDevHealth(r.data)
    } catch {
      // keep previous data
    } finally {
      setHealthLoading(false)
    }
  }, [])

  const toggleDeveloperMode = useCallback(() => {
    setDeveloperMode((prev) => {
      if (!prev && !devHealth) {
        refreshHealth()
      }
      return !prev
    })
  }, [devHealth, refreshHealth])

  const copyDiagnostics = useCallback(() => {
    const h = devHealth || health
    const lines = [
      `LearnMate AI v${h?.version || '2.0.0'}`,
      `Backend: ${h?.backend === 'online' ? 'Online' : 'Offline'}`,
      `Database: ${h?.database === 'online' ? 'Connected' : 'Offline'}`,
      `RAG: ${h?.rag === 'healthy' || h?.rag === 'empty' ? 'Running' : h?.rag === 'disabled' ? 'Disabled' : 'Offline'}`,
      `Environment: ${h?.environment || 'development'}`,
      `Timestamp: ${new Date().toLocaleString()}`,
    ]
    navigator.clipboard.writeText(lines.join('\n')).then(() => {
      toast.success('Diagnostics copied to clipboard')
    }).catch(() => {
      toast.error('Failed to copy diagnostics')
    })
  }, [devHealth, health])

  const handleThemeChange = (mode) => {
    if (mode === 'dark' && !dark) toggleTheme()
    else if (mode === 'light' && dark) toggleTheme()
  }

  const handleSaveLearningPreferences = async () => {
    try {
      await saveStudent({
        learning_style: learningStyle,
        hours_per_week: weeklyGoal,
      })
      localStorage.setItem('learnmate_ai_recommendations', String(aiRecommendations))
      localStorage.setItem('learnmate_study_reminders', String(studyReminders))
      toast.success('Learning preferences saved')
    } catch (e) {
      toast.error(e?.message || 'Failed to save preferences')
    }
  }

  const handleSaveNotifications = () => {
    localStorage.setItem('learnmate_browser_notifications', String(browserNotifications))
    localStorage.setItem('learnmate_email_notifications', String(emailNotifications))
    localStorage.setItem('learnmate_reminder_notifications', String(reminderNotifications))

    if (browserNotifications && 'Notification' in window && Notification.permission !== 'granted') {
      Notification.requestPermission()
    }
    toast.success('Notification preferences saved')
  }

  const handleChangePassword = async () => {
    if (!passwordForm.current_password || !passwordForm.new_password || !passwordForm.confirm_password) {
      toast.error('Please fill in all password fields')
      return
    }
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('New passwords do not match')
      return
    }
    if (passwordForm.new_password.length < 8) {
      toast.error('New password must be at least 8 characters')
      return
    }
    setChangingPassword(true)
    try {
      await authApi.changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
        confirm_password: passwordForm.confirm_password,
      }, accessToken)
      toast.success('Password changed successfully')
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' })
      setShowChangePassword(false)
    } catch (e) {
      toast.error(e?.message || 'Failed to change password')
    } finally {
      setChangingPassword(false)
    }
  }

  const handleResetPassword = async () => {
    const email = user?.email || student?.email
    if (!email) {
      toast.error('No email associated with this account')
      return
    }
    try {
      await authApi.forgotPassword(email)
      toast.success('Password reset link sent to your email')
    } catch (e) {
      toast.error(e?.message || 'Failed to send reset link')
    }
  }

  const handleDelete = async () => {
    try {
      await removeStudent()
      toast.success('Account deleted')
    } catch (e) {
      toast.error(e?.message || 'Failed to delete profile')
    }
    setConfirming(false)
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown'
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric',
      })
    } catch {
      return 'Unknown'
    }
  }

  const displayName = student?.name || user?.full_name || 'Student'
  const displayEmail = user?.email || student?.email || 'No email'
  const displayUsername = user?.username || 'Unknown'
  const memberSince = user?.created_at || null

  const h = devHealth || health
  const dbSize = formatDbSize(h?.database_size_kb)

  return (
    <div className="page-container max-w-3xl">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        <motion.div variants={fadeUp}>
          <h1 className="text-2xl sm:text-3xl font-display font-bold mb-8">Settings</h1>
        </motion.div>

        {/* ── Account ─────────────────────────────────────── */}
        <motion.div variants={fadeUp} className="glass-card p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <HiOutlineUser className="w-5 h-5 text-primary-500" />
            <h2 className="font-semibold">Account</h2>
          </div>
          {student || user ? (
            <div className="space-y-1 divide-y divide-gray-100 dark:divide-gray-800">
              <SettingRow
                icon={HiOutlineUser}
                iconColor="bg-primary-100 dark:bg-primary-900/50 text-primary-600 dark:text-primary-400"
                label="Name"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300">{displayName}</span>
              </SettingRow>
              <SettingRow
                icon={HiOutlineGlobeAlt}
                iconColor="bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400"
                label="Email"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300">{displayEmail}</span>
              </SettingRow>
              <SettingRow
                icon={HiOutlineAcademicCap}
                iconColor="bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400"
                label="Username"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300">@{displayUsername}</span>
              </SettingRow>
              <SettingRow
                icon={HiOutlineClock}
                iconColor="bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-400"
                label="Member Since"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300">{formatDate(memberSince)}</span>
              </SettingRow>
              <SettingRow
                icon={HiOutlineShieldCheck}
                iconColor="bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400"
                label="Account Type"
              >
                <span className="badge-blue">Free</span>
              </SettingRow>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No profile created yet.</p>
          )}
        </motion.div>

        {/* ── Security ────────────────────────────────────── */}
        <motion.div variants={fadeUp} className="glass-card p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <HiOutlineShieldCheck className="w-5 h-5 text-primary-500" />
            <h2 className="font-semibold">Security</h2>
          </div>

          <div className="space-y-1 divide-y divide-gray-100 dark:divide-gray-800">
            {/* Change Password */}
            <div className="py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary-100 dark:bg-primary-900/50 text-primary-600 dark:text-primary-400">
                    <HiOutlineKey className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-medium text-sm">Change Password</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Update your account password</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowChangePassword(!showChangePassword)}
                  className="btn-ghost text-sm flex items-center gap-1"
                >
                  {showChangePassword ? 'Cancel' : 'Change'}
                  {!showChangePassword && <HiOutlineArrowRight className="w-3 h-3" />}
                </button>
              </div>
              <AnimatePresence>
                {showChangePassword && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="mt-4 space-y-3 pl-11">
                      <div className="relative">
                        <input
                          type={showPasswords.current ? 'text' : 'password'}
                          value={passwordForm.current_password}
                          onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                          placeholder="Current password"
                          className="input-field pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPasswords({ ...showPasswords, current: !showPasswords.current })}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                          {showPasswords.current ? <HiOutlineEyeSlash className="w-4 h-4" /> : <HiOutlineEye className="w-4 h-4" />}
                        </button>
                      </div>
                      <div className="relative">
                        <input
                          type={showPasswords.new ? 'text' : 'password'}
                          value={passwordForm.new_password}
                          onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                          placeholder="New password"
                          className="input-field pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPasswords({ ...showPasswords, new: !showPasswords.new })}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                          {showPasswords.new ? <HiOutlineEyeSlash className="w-4 h-4" /> : <HiOutlineEye className="w-4 h-4" />}
                        </button>
                      </div>
                      <div className="relative">
                        <input
                          type={showPasswords.confirm ? 'text' : 'password'}
                          value={passwordForm.confirm_password}
                          onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                          placeholder="Confirm new password"
                          className="input-field pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPasswords({ ...showPasswords, confirm: !showPasswords.confirm })}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                          {showPasswords.confirm ? <HiOutlineEyeSlash className="w-4 h-4" /> : <HiOutlineEye className="w-4 h-4" />}
                        </button>
                      </div>
                      <button
                        onClick={handleChangePassword}
                        disabled={changingPassword}
                        className="btn-primary text-sm py-2 px-4"
                      >
                        {changingPassword ? 'Changing...' : 'Update Password'}
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Reset Password */}
            <SettingRow
              icon={HiOutlineArrowPath}
              iconColor="bg-orange-100 dark:bg-orange-900/50 text-orange-600 dark:text-orange-400"
              label="Reset Password"
              description="Send a reset link to your email"
            >
              <button onClick={handleResetPassword} className="btn-ghost text-sm">
                Send Link
              </button>
            </SettingRow>
          </div>
        </motion.div>

        {/* ── Appearance ──────────────────────────────────── */}
        <motion.div variants={fadeUp} className="glass-card p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <HiOutlineCog6Tooth className="w-5 h-5 text-primary-500" />
            <h2 className="font-semibold">Appearance</h2>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {[
              { mode: 'light', icon: HiOutlineSun, label: 'Light', desc: 'Light mode' },
              { mode: 'dark', icon: HiOutlineMoon, label: 'Dark', desc: 'Dark mode' },
            ].map(({ mode, icon: Icon, label, desc }) => {
              const active = mode === 'dark' ? dark : !dark
              return (
                <button
                  key={mode}
                  onClick={() => handleThemeChange(mode)}
                  className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${
                    active
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/50'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <Icon className={`w-6 h-6 ${active ? 'text-primary-600' : 'text-gray-400'}`} />
                  <div className="text-center">
                    <p className={`text-sm font-medium ${active ? 'text-primary-600' : ''}`}>{label}</p>
                    <p className="text-xs text-gray-500">{desc}</p>
                  </div>
                </button>
              )
            })}
          </div>
        </motion.div>

        {/* ── Learning Preferences ────────────────────────── */}
        <motion.div variants={fadeUp} className="glass-card p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <HiOutlineAcademicCap className="w-5 h-5 text-primary-500" />
            <h2 className="font-semibold">Learning Preferences</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Preferred Learning Style</label>
              <select
                value={learningStyle}
                onChange={(e) => setLearningStyle(e.target.value)}
                className="input-field"
              >
                {LEARNING_STYLES.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Weekly Study Goal</label>
              <select
                value={weeklyGoal}
                onChange={(e) => setWeeklyGoal(Number(e.target.value))}
                className="input-field"
              >
                {WEEKLY_GOALS.map((g) => (
                  <option key={g.value} value={g.value}>{g.label}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1 divide-y divide-gray-100 dark:divide-gray-800">
              <SettingRow
                icon={HiOutlineCheckCircle}
                iconColor="bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-400"
                label="AI Recommendations"
                description="Get personalized learning suggestions"
              >
                <Toggle enabled={aiRecommendations} onChange={setAiRecommendations} />
              </SettingRow>
              <SettingRow
                icon={HiOutlineBell}
                iconColor="bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400"
                label="Study Reminders"
                description="Remind you to study at scheduled times"
              >
                <Toggle enabled={studyReminders} onChange={setStudyReminders} />
              </SettingRow>
            </div>

            <button onClick={handleSaveLearningPreferences} className="btn-primary text-sm py-2 px-4">
              Save Preferences
            </button>
          </div>
        </motion.div>

        {/* ── Notifications ───────────────────────────────── */}
        <motion.div variants={fadeUp} className="glass-card p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <HiOutlineBell className="w-5 h-5 text-primary-500" />
            <h2 className="font-semibold">Notifications</h2>
          </div>

          <div className="space-y-1 divide-y divide-gray-100 dark:divide-gray-800">
            <SettingRow
              icon={HiOutlineGlobeAlt}
              iconColor="bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400"
              label="Browser Notifications"
              description="Receive notifications in your browser"
            >
              <Toggle enabled={browserNotifications} onChange={setBrowserNotifications} />
            </SettingRow>
            <SettingRow
              icon={HiOutlineEnvelope}
              iconColor="bg-cyan-100 dark:bg-cyan-900/50 text-cyan-600 dark:text-cyan-400"
              label="Email Notifications"
              description="Receive updates via email"
            >
              <Toggle enabled={emailNotifications} onChange={setEmailNotifications} />
            </SettingRow>
            <SettingRow
              icon={HiOutlineClock}
              iconColor="bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400"
              label="Study Reminders"
              description="Notifications for scheduled study sessions"
            >
              <Toggle enabled={reminderNotifications} onChange={setReminderNotifications} />
            </SettingRow>
          </div>

          <button onClick={handleSaveNotifications} className="btn-primary text-sm py-2 px-4 mt-4">
            Save Notifications
          </button>
        </motion.div>

        {/* ── About ───────────────────────────────────────── */}
        <motion.div variants={fadeUp} className="glass-card p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <HiOutlineInformationCircle className="w-5 h-5 text-primary-500" />
            <h2 className="font-semibold">About</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-xl gradient-bg flex-shrink-0">
                <HiOutlineAcademicCap className="w-8 h-8 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-display font-bold gradient-text">LearnMate AI</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Version {h?.version || '2.0.0'}
                </p>
              </div>
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              LearnMate AI is a personalized learning platform designed to help learners build
              skills, follow structured roadmaps, discover learning resources, and track progress.
            </p>

            <button
              onClick={toggleDeveloperMode}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors text-sm font-medium w-full justify-between group"
            >
              <div className="flex items-center gap-2.5">
                <HiOutlineCodeBracket className="w-4 h-4 text-gray-400 group-hover:text-primary-500 transition-colors" />
                <span>Developer Mode</span>
              </div>
              <motion.div
                animate={{ rotate: developerMode ? 90 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <HiOutlineChevronRight className="w-4 h-4 text-gray-400" />
              </motion.div>
            </button>
          </div>
        </motion.div>

        {/* ── Developer Mode Panel ────────────────────────── */}
        <AnimatePresence>
          {developerMode && (
            <motion.div
              initial={{ height: 0, opacity: 0, marginBottom: 0 }}
              animate={{ height: 'auto', opacity: 1, marginBottom: 24 }}
              exit={{ height: 0, opacity: 0, marginBottom: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <div className="glass-card p-6 border-dashed border-2 border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-5">
                  <div className="flex items-center gap-2">
                    <HiOutlineServer className="w-5 h-5 text-primary-500" />
                    <h2 className="font-semibold">System Diagnostics</h2>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={copyDiagnostics}
                      className="btn-ghost text-xs flex items-center gap-1.5"
                    >
                      <HiOutlineDocumentDuplicate className="w-3.5 h-3.5" />
                      Copy
                    </button>
                    <button
                      onClick={refreshHealth}
                      disabled={healthLoading}
                      className="btn-ghost text-xs flex items-center gap-1.5"
                    >
                      <HiOutlineArrowPath className={`w-3.5 h-3.5 ${healthLoading ? 'animate-spin' : ''}`} />
                      Refresh
                    </button>
                  </div>
                </div>

                <div className="space-y-2.5">
                  <DiagnosticsRow
                    label="Backend"
                    value={<StatusBadge status={h?.backend || 'disabled'} />}
                  />
                  <DiagnosticsRow
                    label="Database"
                    value={<StatusBadge status={h?.database || 'disabled'} />}
                  />
                  <DiagnosticsRow
                    label="RAG Service"
                    value={<StatusBadge status={h?.rag || 'disabled'} />}
                  />
                  <DiagnosticsRow
                    label="Application Version"
                    value={h?.version || '2.0.0'}
                    mono
                  />
                  <DiagnosticsRow
                    label="Environment"
                    value={
                      <span className={`badge ${
                        h?.environment === 'production'
                          ? 'badge-green'
                          : h?.environment === 'testing'
                          ? 'badge-yellow'
                          : 'badge-blue'
                      }`}>
                        {h?.environment || 'development'}
                      </span>
                    }
                  />

                  {/* Optional details — only shown if available */}
                  {h?.python_version && (
                    <DiagnosticsRow label="Python Version" value={h.python_version} mono />
                  )}
                  {h?.database_type && (
                    <DiagnosticsRow label="Database Type" value={h.database_type} />
                  )}
                  {dbSize && (
                    <DiagnosticsRow label="Database Size" value={dbSize} />
                  )}
                  {h?.indexed_documents !== null && h?.indexed_documents !== undefined && (
                    <DiagnosticsRow label="Indexed Documents" value={h.indexed_documents.toLocaleString()} />
                  )}
                  {h?.server_uptime_seconds !== null && h?.server_uptime_seconds !== undefined && (
                    <DiagnosticsRow label="Server Uptime" value={formatUptime(h.server_uptime_seconds)} />
                  )}
                  {h?.operating_system && (
                    <DiagnosticsRow label="Operating System" value={h.operating_system} />
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Danger Zone ─────────────────────────────────── */}
        <motion.div variants={fadeUp} className="glass-card p-6 border-red-200 dark:border-red-900/50">
          <div className="flex items-center gap-2 mb-4">
            <HiOutlineExclamationTriangle className="w-5 h-5 text-red-500" />
            <h2 className="font-semibold text-red-600 dark:text-red-400">Danger Zone</h2>
          </div>

          {!confirming ? (
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Delete Account</p>
                <p className="text-xs text-gray-500">Permanently delete your account and all associated data</p>
              </div>
              <button
                onClick={() => setConfirming(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 text-sm font-medium hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <HiOutlineTrash className="w-4 h-4" />
                Delete
              </button>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800"
            >
              <div className="flex items-start gap-3">
                <HiOutlineXCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm text-red-700 dark:text-red-400 font-medium mb-1">
                    Are you absolutely sure?
                  </p>
                  <p className="text-xs text-red-600 dark:text-red-400 mb-3">
                    This action cannot be undone. This will permanently delete your profile, roadmap,
                    study sessions, chat history, and all associated data.
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={handleDelete}
                      className="px-4 py-2 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition-colors"
                    >
                      Yes, Delete Everything
                    </button>
                    <button
                      onClick={() => setConfirming(false)}
                      className="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>
      </motion.div>
    </div>
  )
}
