import { useState, useEffect, useMemo, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useForm, Controller } from 'react-hook-form'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  HiOutlineUser, HiOutlineCheckCircle, HiOutlineArrowPath, HiOutlineRocketLaunch,
  HiOutlineAcademicCap, HiOutlineBriefcase, HiOutlineWrench, HiOutlineLightBulb,
  HiOutlineGlobeAlt, HiOutlineClock, HiOutlineFlag, HiOutlineLink, HiOutlineSparkles,
  HiOutlineArrowRight, HiOutlineMagnifyingGlass,
} from 'react-icons/hi2'
import { useApp } from '../context/AppContext'
import { useAuth } from '../context/AuthContext'
import SearchableMultiSelect from '../components/common/SearchableMultiSelect'
import skillsData from '@data/skills_database.json'
import careerRolesData from '@data/career_roles_database.json'

const SKILL_CATEGORIES_DATA = skillsData.categories

const CAREER_ROLES_CATEGORIES_DATA = careerRolesData.categories.map((c) => ({
  name: c.name,
  skills: c.roles,
}))

const CAREER_GOALS = CAREER_ROLES_CATEGORIES_DATA.flatMap((c) => c.skills)

const INTEREST_SUGGESTIONS = [
  'Artificial Intelligence', 'Machine Learning', 'Data Science', 'Web Development',
  'Mobile Development', 'Cloud Computing', 'DevOps', 'Cybersecurity', 'UI/UX',
  'Blockchain', 'Robotics', 'IoT', 'Game Development', 'Backend Development',
  'Frontend Development', 'Full Stack', 'Natural Language Processing', 'Computer Vision',
  'Big Data', 'AR/VR',
]

const STUDY_TIMES = ['Morning', 'Afternoon', 'Evening', 'Night']

const JOB_ROLES_CATEGORIES_DATA = CAREER_ROLES_CATEGORIES_DATA

const COMPANIES = [
  'Google', 'Microsoft', 'Amazon', 'IBM', 'OpenAI', 'Meta', 'Apple',
  'Netflix', 'NVIDIA', 'Infosys', 'TCS', 'Wipro', 'Startup', 'Other',
]

const CURRENT_GOALS = [
  'Get Internship', 'Crack Campus Placement', 'Build Portfolio',
  'Prepare for Hackathons', 'Learn New Technology', 'Build Final Year Project',
  'Open Source Contributions',
]

const EXPERIENCE_LEVELS = ['Student', 'Fresher', 'Intern', 'Working Professional']

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.06 } } }

function CardSection({ number, icon: Icon, title, children }) {
  return (
    <motion.div variants={fadeUp} className="glass-card p-6 space-y-5">
      <h2 className="text-lg font-semibold flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
          <Icon className="w-4 h-4 text-primary-600" />
        </div>
        <span>{title}</span>
        <span className="text-xs font-normal text-gray-400 dark:text-gray-500 ml-auto">Step {number}</span>
      </h2>
      {children}
    </motion.div>
  )
}

function FieldLabel({ label, required }) {
  return (
    <label className="block text-sm font-medium mb-1.5">
      {label}
      {required && <span className="text-red-500 ml-0.5">*</span>}
    </label>
  )
}

function ValidationMsg({ error }) {
  if (!error) return null
  return <p className="text-red-500 text-xs mt-1">{error.message}</p>
}

function TagInput({ label, suggestions, value, onChange, placeholder, required, error }) {
  const [input, setInput] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)

  const filtered = suggestions.filter(
    (s) => s.toLowerCase().includes(input.toLowerCase()) && !value.includes(s)
  )

  const addTag = (tag) => {
    if (tag && !value.includes(tag)) {
      onChange([...value, tag])
    }
    setInput('')
    setShowSuggestions(false)
  }

  const removeTag = (tag) => onChange(value.filter((t) => t !== tag))

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') { e.preventDefault(); addTag(input.trim()) }
    if (e.key === 'Backspace' && !input && value.length) removeTag(value[value.length - 1])
  }

  return (
    <div className="space-y-2">
      <FieldLabel label={label} required={required} />
      <div className={`input-field flex flex-wrap gap-2 min-h-[48px] !py-2 focus-within:ring-2 focus-within:ring-primary-500 ${error ? 'ring-2 ring-red-500' : ''}`}>
        <AnimatePresence mode="popLayout">
          {value.map((tag) => (
            <motion.span
              key={tag}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              layout
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-sm font-medium"
            >
              {tag}
              <button type="button" onClick={() => removeTag(tag)} className="hover:text-red-500 ml-0.5">&times;</button>
            </motion.span>
          ))}
        </AnimatePresence>
        <input
          type="text"
          value={input}
          onChange={(e) => { setInput(e.target.value); setShowSuggestions(true) }}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          onKeyDown={handleKeyDown}
          placeholder={value.length ? '' : placeholder}
          className="flex-1 min-w-[120px] bg-transparent outline-none text-sm"
        />
      </div>
      {showSuggestions && filtered.length > 0 && (
        <div className="relative z-20">
          <div className="absolute top-0 left-0 right-0 max-h-48 overflow-y-auto bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg mt-1 p-2 flex flex-wrap gap-1.5">
            {filtered.slice(0, 15).map((s) => (
              <button key={s} type="button" onMouseDown={() => addTag(s)}
                className="px-3 py-1.5 rounded-lg text-sm bg-gray-100 dark:bg-gray-700 hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors">
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
      <ValidationMsg error={error} />
    </div>
  )
}

function ChipSelect({ label, options, value, onChange, required, error, multiple = false }) {
  const isSelected = (opt) => {
    if (multiple) return value.includes(opt)
    return value === opt
  }
  const toggle = (opt) => {
    if (multiple) {
      onChange(isSelected(opt) ? value.filter((v) => v !== opt) : [...value, opt])
    } else {
      onChange(value === opt ? '' : opt)
    }
  }
  return (
    <div className="space-y-2">
      <FieldLabel label={label} required={required} />
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => (
          <button
            key={opt}
            type="button"
            onClick={() => toggle(opt)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all border ${
              isSelected(opt)
                ? 'bg-primary-500 text-white border-primary-500 shadow-sm'
                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700'
            }`}
          >
            {opt}
          </button>
        ))}
      </div>
      <ValidationMsg error={error} />
    </div>
  )
}

function SliderInput({ label, value, onChange, min = 1, max = 40, unit = 'hours/week' }) {
  return (
    <div className="space-y-2">
      <FieldLabel label={label} />
      <div className="flex items-center gap-4">
        <input
          type="range"
          min={min}
          max={max}
          step={1}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="flex-1 accent-primary-600 h-2"
        />
        <span className="w-20 text-center font-bold text-lg text-primary-600 dark:text-primary-400">{value} {unit}</span>
      </div>
      <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500">
        <span>{min}h</span>
        <span>{max}h</span>
      </div>
    </div>
  )
}

function GoalCheckbox({ label, checked, onChange }) {
  return (
    <button
      type="button"
      onClick={onChange}
      className={`flex items-center gap-3 p-3.5 rounded-xl border-2 cursor-pointer transition-all text-left group ${
        checked
          ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-500 shadow-sm'
          : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 hover:bg-gray-50 dark:hover:bg-gray-800/50'
      }`}
    >
      <div className={`w-5 h-5 rounded flex items-center justify-center border-2 transition-all shrink-0 ${
        checked
          ? 'bg-primary-500 border-primary-500 scale-110'
          : 'border-gray-300 dark:border-gray-600 group-hover:border-primary-400'
      }`}>
        {checked && (
          <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>
      <span className={`text-sm font-medium transition-colors ${checked ? 'text-primary-700 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'}`}>
        {label}
      </span>
    </button>
  )
}

function ProgressStep({ label, status }) {
  return (
    <div className="flex items-center gap-3 py-1">
      <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 transition-all duration-300 ${
        status === 'done'
          ? 'bg-green-500 text-white'
          : status === 'active'
            ? 'bg-primary-500 text-white animate-pulse'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500'
      }`}>
        {status === 'done' ? (
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        ) : status === 'active' ? (
          <HiOutlineArrowPath className="w-3 h-3 animate-spin" />
        ) : (
          <span className="text-[10px] font-bold">○</span>
        )}
      </div>
      <span className={`text-sm transition-colors duration-300 ${
        status === 'done'
          ? 'text-green-600 dark:text-green-400 font-medium'
          : status === 'active'
            ? 'text-primary-700 dark:text-primary-300 font-medium'
            : 'text-gray-400 dark:text-gray-500'
      }`}>
        {label}
      </span>
    </div>
  )
}

function ProfileCompletionBar({ percentage }) {
  const getColor = (pct) => {
    if (pct >= 80) return 'from-green-400 to-emerald-500'
    if (pct >= 50) return 'from-primary-400 to-primary-600'
    if (pct >= 25) return 'from-yellow-400 to-orange-500'
    return 'from-gray-300 to-gray-400'
  }
  const getMessage = (pct) => {
    if (pct >= 90) return "Your profile is nearly complete! You'll receive highly personalised recommendations."
    if (pct >= 70) return "Great progress! A few more details will improve your AI recommendations."
    if (pct >= 40) return "Your roadmap becomes more accurate with more profile information."
    return "Complete your profile to receive better AI recommendations."
  }
  return (
    <motion.div variants={fadeUp} className="glass-card p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <HiOutlineSparkles className="w-4 h-4 text-primary-500" />
          <span className="text-sm font-semibold">Profile Completion</span>
        </div>
        <span className="text-sm font-bold text-primary-600 dark:text-primary-400">{Math.round(percentage)}%</span>
      </div>
      <div className="w-full h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-3">
        <motion.div
          className={`h-full rounded-full bg-gradient-to-r ${getColor(percentage)}`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400">{getMessage(percentage)}</p>
    </motion.div>
  )
}

function URLField({ label, value, onChange, placeholder, error }) {
  return (
    <div>
      <FieldLabel label={label} />
      <div className="relative">
        <HiOutlineGlobeAlt className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="url"
          value={value || ''}
          onChange={(e) => onChange(e.target.value || null)}
          placeholder={placeholder}
          className={`input-field !pl-10 ${error ? 'ring-2 ring-red-500' : ''}`}
        />
      </div>
      <ValidationMsg error={error} />
    </div>
  )
}

const ROADMAP_PHASES = {
  IDLE: 'idle',
  SAVING: 'saving',
  SAVED: 'saved',
  GENERATING: 'generating',
  SUCCESS: 'success',
  ERROR: 'error',
}

const GENERATION_MESSAGES = [
  'Analyzing your skills...',
  'Matching your career goal...',
  'Finding recommended courses...',
  'Building your personalized roadmap...',
  'Almost finished...',
]

export default function Profile() {
  const { student, saveStudent, buildRoadmap, initialized } = useApp()
  const { user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [saving, setSaving] = useState(false)
  const [roadmapPhase, setRoadmapPhase] = useState(ROADMAP_PHASES.IDLE)
  const [roadmapError, setRoadmapError] = useState(null)
  const [generationMsg, setGenerationMsg] = useState(GENERATION_MESSAGES[0])
  const [genStep, setGenStep] = useState(0)

  // Accept career goal from career test redirect
  const careerGoalFromTest = location.state?.careerGoal || ''
  const fromCareerTest = location.state?.fromCareerTest || false

  const { register, handleSubmit, reset, watch, setValue, control, trigger, getValues, formState: { errors } } = useForm({
    defaultValues: {
      name: '',
      email: '',
      career_goal: '',
      skill_level: 'beginner',
      current_skills: [],
      interests: [],
      learning_style: '',
      hours_per_week: 10,
      preferred_study_time: '',
      preferred_job_role: '',
      dream_company: '',
      current_goals: [],
      experience_level: '',
      github_url: '',
      linkedin_url: '',
    },
  })

  useEffect(() => {
    if (student) {
      reset({
        name: student.name || '',
        email: student.email || '',
        career_goal: careerGoalFromTest || student.career_goal || '',
        skill_level: (student.skill_level || 'beginner').toLowerCase(),
        current_skills: student.current_skills || [],
        interests: student.interests || [],
        learning_style: student.learning_style || '',
        hours_per_week: student.hours_per_week || 10,
        preferred_study_time: student.preferred_study_time || '',
        preferred_job_role: careerGoalFromTest || student.preferred_job_role || '',
        dream_company: student.dream_company || '',
        current_goals: student.current_goals || [],
        experience_level: student.experience_level || '',
        github_url: student.github_url || '',
        linkedin_url: student.linkedin_url || '',
      })
    } else if (careerGoalFromTest) {
      // Pre-fill career goal even if no student profile exists yet
      setValue('career_goal', careerGoalFromTest)
      setValue('preferred_job_role', careerGoalFromTest)
    }
  }, [student, reset, careerGoalFromTest, setValue])

  const formValues = watch()
  const watchedSkills = watch('current_skills') || []
  const watchedInterests = watch('interests') || []
  const watchedGoals = watch('current_goals') || []
  const watchedHours = watch('hours_per_week') || 10

  const completionPercentage = useMemo(() => {
    let filled = 0
    let total = 12
    if (formValues.name?.trim()) filled++
    if (formValues.career_goal?.trim()) filled++
    if (formValues.email?.trim()) filled++
    if (formValues.current_skills?.length > 0) filled++
    if (formValues.interests?.length > 0) filled++
    if (formValues.learning_style) filled++
    if (formValues.preferred_study_time) filled++
    if (formValues.preferred_job_role) filled++
    if (formValues.dream_company) filled++
    if (formValues.current_goals?.length > 0) filled++
    if (formValues.experience_level) filled++
    if (formValues.github_url?.trim() || formValues.linkedin_url?.trim()) filled++
    return (filled / total) * 100
  }, [formValues])

  useEffect(() => {
    if (roadmapPhase !== ROADMAP_PHASES.GENERATING) return
    const interval = setInterval(() => {
      setGenStep((prev) => {
        const next = Math.min(prev + 1, GENERATION_MESSAGES.length - 1)
        setGenerationMsg(GENERATION_MESSAGES[next])
        return next
      })
    }, 3000)
    return () => clearInterval(interval)
  }, [roadmapPhase])

  const onSubmit = async (data) => {
    setSaving(true)
    try {
      await saveStudent(data)
      toast.success('Profile saved!')
    } catch (e) {
      toast.error(e?.message || 'Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  const onGenerateRoadmap = async () => {
    const valid = await trigger()
    if (!valid) { toast.error('Fix validation errors first'); return }

    setRoadmapError(null)
    setGenStep(0)
    setGenerationMsg(GENERATION_MESSAGES[0])
    const t0 = performance.now()

    // Step 1: Save profile
    setRoadmapPhase(ROADMAP_PHASES.SAVING)
    const data = getValues()
    try {
      const tSaveStart = performance.now()
      await saveStudent(data)
      const tSaveDone = performance.now()
      console.log(`Profile Save: ${(tSaveDone - tSaveStart).toFixed(0)} ms`)

      setRoadmapPhase(ROADMAP_PHASES.SAVED)
      await new Promise((r) => setTimeout(r, 1000))

      // Step 2: Generate roadmap
      setRoadmapPhase(ROADMAP_PHASES.GENERATING)
      const tGenStart = performance.now()
      await buildRoadmap({ weeks: 12, hours_per_week: data.hours_per_week })
      const tGenDone = performance.now()
      console.log(`Roadmap Request: ${((tGenDone - tGenStart) / 1000).toFixed(1)} s`)

      setRoadmapPhase(ROADMAP_PHASES.SUCCESS)
      await new Promise((r) => setTimeout(r, 1000))

      const tNav = performance.now()
      console.log(`Navigation: ${(tNav - tGenDone).toFixed(0)} ms`)
      console.log(`Total: ${((tNav - t0) / 1000).toFixed(1)} s`)
      navigate('/roadmap')
    } catch (e) {
      const reason = e?.message || e?.response?.data?.detail || 'Network error. Please try again.'
      setRoadmapError(reason)
      setRoadmapPhase(ROADMAP_PHASES.ERROR)
    }
  }

  return (
    <div className="page-container max-w-3xl">
      {!initialized ? (
        <div className="flex flex-col items-center justify-center py-20">
          <HiOutlineArrowPath className="w-8 h-8 text-primary-500 animate-spin mb-4" />
          <p className="text-gray-500 dark:text-gray-400 text-sm">Loading your learning profile...</p>
        </div>
      ) : (
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        <motion.div variants={fadeUp} className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-display font-bold mb-2">
            {student ? 'Edit Profile' : 'Create Your Profile'}
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            Tell us about yourself so we can personalise your learning experience.
          </p>
        </motion.div>

        <ProfileCompletionBar percentage={completionPercentage} />

        {/* Career Test Result Banner */}
        {fromCareerTest && careerGoalFromTest && (
          <motion.div variants={fadeUp} className="glass-card p-4 mt-4 border-2 border-primary-200 dark:border-primary-800/50">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shrink-0">
                <HiOutlineSparkles className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold">Career goal set from Career Aptitude Test</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Your career goal has been set to <span className="font-semibold text-primary-600">{careerGoalFromTest}</span>.
                  Save your profile and generate a roadmap to get started!
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {user && (
          <motion.div variants={fadeUp} className="glass-card p-4 mt-6 flex items-center gap-3">
            {user.avatar_url ? (
              <img src={user.avatar_url} alt="" className="w-10 h-10 rounded-full" />
            ) : (
              <div className="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                <span className="text-primary-600 font-semibold text-lg">
                  {user.full_name?.charAt(0)?.toUpperCase() || user.username?.charAt(0)?.toUpperCase()}
                </span>
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate">{user.full_name}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
            </div>
            <span className="badge badge-green">
              Email
            </span>
          </motion.div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 mt-6" onKeyDown={(e) => { if (roadmapPhase !== ROADMAP_PHASES.IDLE && roadmapPhase !== ROADMAP_PHASES.ERROR) e.preventDefault() }}>
          {/* Section 1: Basic Information */}
          <CardSection number={1} icon={HiOutlineUser} title="Basic Information">
            <div>
              <FieldLabel label="Full Name" required />
              <input
                {...register('name', { required: 'Name is required', minLength: { value: 1, message: 'Name is required' } })}
                className={`input-field ${errors.name ? 'ring-2 ring-red-500' : ''}`}
                placeholder="Alice Johnson"
              />
              <ValidationMsg error={errors.name} />
            </div>

            <div>
              <FieldLabel label="Email Address" />
              <input
                type="email"
                {...register('email', {
                  pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Enter a valid email' }
                })}
                className={`input-field ${errors.email ? 'ring-2 ring-red-500' : ''}`}
                placeholder="alice@example.com"
              />
              <ValidationMsg error={errors.email} />
            </div>

            <div>
              <FieldLabel label="Skill Level" />
              <div className="flex gap-3">
                {['Beginner', 'Intermediate', 'Advanced'].map((level) => (
                  <label key={level} className="flex-1">
                    <input
                      type="radio"
                      value={level.toLowerCase()}
                      {...register('skill_level')}
                      className="sr-only peer"
                    />
                    <div className="p-3 rounded-xl border-2 border-gray-200 dark:border-gray-700 text-center cursor-pointer transition-all peer-checked:border-primary-500 peer-checked:bg-primary-50 dark:peer-checked:bg-primary-900/20 hover:border-gray-300 dark:hover:border-gray-600">
                      <span className="text-sm font-medium">{level}</span>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </CardSection>

          {/* Section 2: Skills & Interests */}
          <CardSection number={2} icon={HiOutlineWrench} title="Skills & Interests">
            <SearchableMultiSelect
              label="Current Skills"
              categories={SKILL_CATEGORIES_DATA}
              value={watchedSkills}
              onChange={(v) => setValue('current_skills', v)}
              placeholder="Search and select your skills..."
              maxSelections={20}
              allowCustom={true}
              customPlaceholder="Add a custom skill..."
              required
            />

            <TagInput
              label="Interests"
              suggestions={INTEREST_SUGGESTIONS}
              value={watchedInterests}
              onChange={(v) => setValue('interests', v)}
              placeholder="Type or select interests..."
            />
          </CardSection>

          {/* Section 3: Learning Preferences */}
          <CardSection number={3} icon={HiOutlineLightBulb} title="Learning Preferences">
            <div>
              <FieldLabel label="Learning Style" />
              <div className="grid grid-cols-2 gap-3">
                {[
                  { value: 'video', label: 'Video Courses', icon: '🎬' },
                  { value: 'reading', label: 'Reading', icon: '📖' },
                  { value: 'hands-on', label: 'Hands-on Projects', icon: '🛠' },
                  { value: 'mixed', label: 'Mixed Learning', icon: '🔀' },
                ].map((style) => (
                  <label key={style.value} className="cursor-pointer">
                    <input
                      type="radio"
                      value={style.value}
                      {...register('learning_style')}
                      className="sr-only peer"
                    />
                    <div className="p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 text-center transition-all peer-checked:border-primary-500 peer-checked:bg-primary-50 dark:peer-checked:bg-primary-900/20 hover:border-gray-300 dark:hover:border-gray-600">
                      <span className="text-xl block mb-1">{style.icon}</span>
                      <span className="text-sm font-medium">{style.label}</span>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <FieldLabel label="Preferred Study Time" />
              <select {...register('preferred_study_time')} className="input-field">
                <option value="">Select...</option>
                {STUDY_TIMES.map((t) => <option key={t} value={t.toLowerCase()}>{t}</option>)}
              </select>
            </div>

            <SliderInput
              label="Hours Available Per Week"
              value={watchedHours}
              onChange={(v) => setValue('hours_per_week', v)}
            />
          </CardSection>

          {/* Section 4: Career Preferences */}
          <CardSection number={4} icon={HiOutlineBriefcase} title="Career Preferences">
            <div>
              <FieldLabel label="Career Goal" required />
              <SearchableMultiSelect
                label=""
                categories={JOB_ROLES_CATEGORIES_DATA}
                value={formValues.career_goal ? [formValues.career_goal] : []}
                onChange={(v) => setValue('career_goal', v[v.length - 1] || '')}
                placeholder="Search career goals..."
                maxSelections={1}
                allowCustom={true}
                customPlaceholder="Add a custom career goal..."
              />
              {errors.career_goal && <p className="text-red-500 text-xs mt-1">{errors.career_goal.message}</p>}
            </div>

            <div>
              <FieldLabel label="Preferred Job Role" />
              <SearchableMultiSelect
                label=""
                categories={JOB_ROLES_CATEGORIES_DATA}
                value={formValues.preferred_job_role ? [formValues.preferred_job_role] : []}
                onChange={(v) => setValue('preferred_job_role', v[v.length - 1] || '')}
                placeholder="Search job roles..."
                maxSelections={1}
                allowCustom={true}
                customPlaceholder="Add a custom role..."
              />
            </div>

            <div>
              <FieldLabel label="Dream Company" />
              <select {...register('dream_company')} className="input-field">
                <option value="">Select...</option>
                {COMPANIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </CardSection>

          {/* Section 5: Current Goals */}
          <CardSection number={5} icon={HiOutlineFlag} title="Current Goals">
            <div className="flex items-center justify-between mb-1">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Selected Goals: <span className="font-semibold text-primary-600 dark:text-primary-400">{watchedGoals.length}</span> of {CURRENT_GOALS.length}
              </p>
              {watchedGoals.length === 0 && (
                <p className="text-xs text-amber-600 dark:text-amber-400 font-medium">Select at least one goal</p>
              )}
            </div>
            <div className="grid sm:grid-cols-2 gap-2.5">
              {CURRENT_GOALS.map((goal) => (
                <GoalCheckbox
                  key={goal}
                  label={goal}
                  checked={watchedGoals.includes(goal)}
                  onChange={() => {
                    const current = watchedGoals
                    setValue('current_goals', current.includes(goal) ? current.filter((g) => g !== goal) : [...current, goal], { shouldValidate: true })
                  }}
                />
              ))}
            </div>
          </CardSection>

          {/* Section 6: Experience */}
          <CardSection number={6} icon={HiOutlineAcademicCap} title="Experience">
            <ChipSelect
              label="Current Experience Level"
              options={EXPERIENCE_LEVELS}
              value={formValues.experience_level || ''}
              onChange={(v) => setValue('experience_level', v)}
            />
          </CardSection>

          {/* Section 7: Social Links */}
          <CardSection number={7} icon={HiOutlineLink} title="Social Links (Optional)">
            <URLField
              label="GitHub Profile URL"
              value={formValues.github_url}
              onChange={(v) => setValue('github_url', v)}
              placeholder="https://github.com/username"
            />
            <URLField
              label="LinkedIn Profile URL"
              value={formValues.linkedin_url}
              onChange={(v) => setValue('linkedin_url', v)}
              placeholder="https://linkedin.com/in/username"
            />
          </CardSection>

          {/* Actions & Progress */}
          <motion.div variants={fadeUp} className="space-y-4 pb-8">
            {/* Progress Indicator (visible during save/generate flow) */}
            <AnimatePresence>
              {roadmapPhase !== ROADMAP_PHASES.IDLE && roadmapPhase !== ROADMAP_PHASES.ERROR && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="glass-card p-5 space-y-3">
                    <h3 className="text-sm font-semibold flex items-center gap-2">
                      {roadmapPhase === ROADMAP_PHASES.SUCCESS ? (
                        <><HiOutlineCheckCircle className="w-5 h-5 text-green-500" /> Roadmap Ready</>
                      ) : (
                        <><HiOutlineSparkles className="w-5 h-5 text-primary-500 animate-pulse" /> Generating Your Roadmap</>
                      )}
                    </h3>

                    <div className="space-y-2">
                      {/* Step: Saving Profile */}
                      <ProgressStep
                        label="Saving Profile"
                        status={
                          roadmapPhase === ROADMAP_PHASES.SAVING ? 'active' :
                          [ROADMAP_PHASES.SAVED, ROADMAP_PHASES.GENERATING, ROADMAP_PHASES.SUCCESS].includes(roadmapPhase) ? 'done' :
                          'pending'
                        }
                      />

                      {/* Step: Analyzing Skills */}
                      <ProgressStep
                        label="Analyzing Skills"
                        status={
                          roadmapPhase === ROADMAP_PHASES.GENERATING && genStep >= 0 ? 'active' :
                          [ROADMAP_PHASES.SUCCESS].includes(roadmapPhase) ? 'done' :
                          'pending'
                        }
                      />

                      {/* Step: Finding Courses */}
                      <ProgressStep
                        label="Finding Best Courses"
                        status={
                          roadmapPhase === ROADMAP_PHASES.GENERATING && genStep >= 2 ? 'active' :
                          roadmapPhase === ROADMAP_PHASES.SUCCESS ? 'done' :
                          'pending'
                        }
                      />

                      {/* Step: Creating Weekly Plan */}
                      <ProgressStep
                        label="Creating Weekly Plan"
                        status={
                          roadmapPhase === ROADMAP_PHASES.GENERATING && genStep >= 3 ? 'active' :
                          roadmapPhase === ROADMAP_PHASES.SUCCESS ? 'done' :
                          'pending'
                        }
                      />

                      {/* Step: Finalizing */}
                      <ProgressStep
                        label="Finalizing Roadmap"
                        status={
                          roadmapPhase === ROADMAP_PHASES.GENERATING && genStep >= 4 ? 'active' :
                          roadmapPhase === ROADMAP_PHASES.SUCCESS ? 'done' :
                          'pending'
                        }
                      />
                    </div>

                    {roadmapPhase === ROADMAP_PHASES.GENERATING && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1.5 pl-1">
                        <HiOutlineSparkles className="w-3 h-3 animate-pulse text-primary-500" />
                        {generationMsg}
                      </p>
                    )}

                    {roadmapPhase === ROADMAP_PHASES.SUCCESS && (
                      <p className="text-xs text-green-600 dark:text-green-400 font-medium flex items-center gap-1.5 pl-1">
                        <HiOutlineCheckCircle className="w-3.5 h-3.5" />
                        Redirecting to your roadmap...
                      </p>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Error State */}
            <AnimatePresence>
              {roadmapPhase === ROADMAP_PHASES.ERROR && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="glass-card p-5 border-2 border-red-200 dark:border-red-800/50 space-y-3">
                    <h3 className="text-sm font-semibold text-red-600 dark:text-red-400 flex items-center gap-2">
                      <span className="text-lg">✕</span> Failed to Generate Roadmap
                    </h3>
                    <p className="text-xs text-red-500 dark:text-red-400">{roadmapError}</p>
                    <button
                      type="button"
                      onClick={() => { setRoadmapPhase(ROADMAP_PHASES.IDLE); setRoadmapError(null) }}
                      className="text-xs font-medium text-primary-600 dark:text-primary-400 hover:underline"
                    >
                      Retry
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                type="submit"
                disabled={saving || roadmapPhase !== ROADMAP_PHASES.IDLE}
                className="btn-primary flex items-center justify-center gap-2 min-w-[160px] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? (
                  <><HiOutlineArrowPath className="w-5 h-5 animate-spin" /> Saving...</>
                ) : (
                  <><HiOutlineCheckCircle className="w-5 h-5" /> Save Profile</>
                )}
              </button>
              <button
                type="button"
                onClick={() => {
                  reset({
                    name: '', email: '', career_goal: '', skill_level: 'beginner',
                    current_skills: [], interests: [], learning_style: '', hours_per_week: 10,
                    preferred_study_time: '', preferred_job_role: '', dream_company: '',
                    current_goals: [], experience_level: '', github_url: '', linkedin_url: '',
                  })
                  toast.success('Form reset')
                }}
                disabled={roadmapPhase !== ROADMAP_PHASES.IDLE && roadmapPhase !== ROADMAP_PHASES.ERROR}
                className="btn-ghost disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Reset
              </button>
              <button
                type="button"
                onClick={onGenerateRoadmap}
                disabled={roadmapPhase !== ROADMAP_PHASES.IDLE && roadmapPhase !== ROADMAP_PHASES.ERROR}
                className="btn-secondary flex items-center justify-center gap-2 ml-auto disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {roadmapPhase === ROADMAP_PHASES.GENERATING ? (
                  <><HiOutlineArrowPath className="w-5 h-5 animate-spin" /> Generating...</>
                ) : roadmapPhase === ROADMAP_PHASES.SUCCESS ? (
                  <><HiOutlineCheckCircle className="w-5 h-5" /> Done</>
                ) : (
                  <><HiOutlineRocketLaunch className="w-5 h-5" /> Generate Roadmap <HiOutlineArrowRight className="w-4 h-4" /></>
                )}
              </button>
            </div>
          </motion.div>
        </form>
      </motion.div>
      )}
    </div>
  )
}
