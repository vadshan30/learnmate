import { useState, useEffect, useMemo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
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

const CAREER_GOALS = [
  'AI Engineer', 'Machine Learning Engineer', 'Data Scientist', 'Data Engineer',
  'Software Engineer', 'Full Stack Developer', 'Frontend Developer', 'Backend Developer',
  'DevOps Engineer', 'Cloud Engineer', 'Cybersecurity Engineer', 'Mobile App Developer',
  'UI/UX Designer', 'Other',
]

const SKILL_CATEGORIES = {
  Programming: ['Python', 'Java', 'C++', 'JavaScript', 'TypeScript', 'SQL', 'Go', 'Rust', 'Ruby', 'PHP'],
  Frontend: ['HTML', 'CSS', 'React', 'Angular', 'Vue', 'Svelte', 'Tailwind CSS', 'Bootstrap'],
  Backend: ['Node.js', 'Express', 'FastAPI', 'Spring Boot', 'Django', 'Flask', 'Ruby on Rails'],
  'AI / Data': ['Machine Learning', 'Deep Learning', 'NLP', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn', 'OpenCV', 'Keras'],
  Cloud: ['Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Terraform', 'Jenkins', 'GitHub Actions'],
  'Tools & Other': ['Git', 'GitHub', 'Linux', 'SQL', 'MongoDB', 'PostgreSQL', 'Redis', 'GraphQL', 'REST APIs'],
}

const INTEREST_SUGGESTIONS = [
  'Artificial Intelligence', 'Machine Learning', 'Data Science', 'Web Development',
  'Mobile Development', 'Cloud Computing', 'DevOps', 'Cybersecurity', 'UI/UX',
  'Blockchain', 'Robotics', 'IoT', 'Game Development', 'Backend Development',
  'Frontend Development', 'Full Stack', 'Natural Language Processing', 'Computer Vision',
  'Big Data', 'AR/VR',
]

const STUDY_TIMES = ['Morning', 'Afternoon', 'Evening', 'Night']

const JOB_ROLES = [
  'AI Engineer', 'Data Scientist', 'ML Engineer', 'Data Engineer',
  'Full Stack Developer', 'Backend Developer', 'Frontend Developer',
  'DevOps Engineer', 'Cloud Engineer',
]

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

export default function Profile() {
  const { student, saveStudent, buildRoadmap } = useApp()
  const navigate = useNavigate()
  const [saving, setSaving] = useState(false)
  const [skillSearch, setSkillSearch] = useState('')

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
        career_goal: student.career_goal || '',
        skill_level: (student.skill_level || 'beginner').toLowerCase(),
        current_skills: student.current_skills || [],
        interests: student.interests || [],
        learning_style: student.learning_style || '',
        hours_per_week: student.hours_per_week || 10,
        preferred_study_time: student.preferred_study_time || '',
        preferred_job_role: student.preferred_job_role || '',
        dream_company: student.dream_company || '',
        current_goals: student.current_goals || [],
        experience_level: student.experience_level || '',
        github_url: student.github_url || '',
        linkedin_url: student.linkedin_url || '',
      })
    }
  }, [student, reset])

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

  const filteredSkillCategories = useMemo(() => {
    if (!skillSearch.trim()) return SKILL_CATEGORIES
    const q = skillSearch.toLowerCase()
    const result = {}
    for (const [cat, skills] of Object.entries(SKILL_CATEGORIES)) {
      const matches = skills.filter((s) => s.toLowerCase().includes(q))
      if (matches.length > 0 || cat.toLowerCase().includes(q)) result[cat] = matches.length > 0 ? matches : skills
    }
    return result
  }, [skillSearch])

  const addSkill = useCallback((skill) => {
    const current = watch('current_skills') || []
    if (!current.includes(skill)) setValue('current_skills', [...current, skill])
  }, [watch, setValue])

  const removeSkill = useCallback((skill) => {
    const current = watch('current_skills') || []
    setValue('current_skills', current.filter((s) => s !== skill))
  }, [watch, setValue])

  const onSubmit = async (data) => {
    setSaving(true)
    try {
      await saveStudent(data)
    } catch (e) {
      toast.error(e?.message || 'Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  const onGenerateRoadmap = async () => {
    const valid = await trigger()
    if (!valid) { toast.error('Fix validation errors first'); return }
    const data = getValues()
    setSaving(true)
    try {
      await saveStudent(data)
      await buildRoadmap({ weeks: 12, hours_per_week: data.hours_per_week })
      navigate('/roadmap')
    } catch (e) {
      toast.error(e?.message || 'Failed to generate roadmap')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page-container max-w-3xl">
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

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 mt-6">
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
              <FieldLabel label="Career Goal" required />
              <select
                {...register('career_goal', { required: 'Career goal is required' })}
                className={`input-field ${errors.career_goal ? 'ring-2 ring-red-500' : ''}`}
              >
                <option value="">Select your career goal...</option>
                {CAREER_GOALS.map((g) => <option key={g} value={g}>{g}</option>)}
              </select>
              <ValidationMsg error={errors.career_goal} />
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
            <div className="space-y-4">
              <div className="relative">
                <HiOutlineMagnifyingGlass className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={skillSearch}
                  onChange={(e) => setSkillSearch(e.target.value)}
                  placeholder="Search skills..."
                  className="input-field !pl-10"
                />
              </div>

              {Object.entries(filteredSkillCategories).map(([category, skills]) => (
                <div key={category}>
                  <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">{category}</h4>
                  <div className="flex flex-wrap gap-2">
                    {skills.map((skill) => {
                      const isSelected = watchedSkills.includes(skill)
                      return (
                        <button
                          key={skill}
                          type="button"
                          onClick={() => isSelected ? removeSkill(skill) : addSkill(skill)}
                          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all border ${
                            isSelected
                              ? 'bg-primary-500 text-white border-primary-500 shadow-sm'
                              : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700'
                          }`}
                        >
                          {isSelected && <HiOutlineCheckCircle className="w-3 h-3 inline mr-1" />}
                          {skill}
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}

              <AnimatePresence mode="popLayout">
                {watchedSkills.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="overflow-hidden"
                  >
                    <h4 className="text-xs font-semibold text-primary-600 dark:text-primary-400 mb-2">Selected Skills ({watchedSkills.length})</h4>
                    <div className="flex flex-wrap gap-1.5">
                      {watchedSkills.map((skill) => (
                        <motion.span
                          key={skill}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.8 }}
                          layout
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-sm font-medium"
                        >
                          {skill}
                          <button type="button" onClick={() => removeSkill(skill)} className="hover:text-red-500">&times;</button>
                        </motion.span>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

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
              <FieldLabel label="Preferred Job Role" />
              <select {...register('preferred_job_role')} className="input-field">
                <option value="">Select...</option>
                {JOB_ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
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

          {/* Actions */}
          <motion.div variants={fadeUp} className="flex flex-col sm:flex-row gap-3 pb-8">
            <button
              type="submit"
              disabled={saving}
              className="btn-primary flex items-center justify-center gap-2 min-w-[160px]"
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
              className="btn-ghost"
            >
              Reset
            </button>
            <button
              type="button"
              onClick={onGenerateRoadmap}
              disabled={saving}
              className="btn-secondary flex items-center justify-center gap-2 ml-auto"
            >
              <HiOutlineRocketLaunch className="w-5 h-5" /> Generate Roadmap
              <HiOutlineArrowRight className="w-4 h-4" />
            </button>
          </motion.div>
        </form>
      </motion.div>
    </div>
  )
}
