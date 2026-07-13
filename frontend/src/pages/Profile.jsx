import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { HiOutlineCheckCircle, HiOutlineArrowPath, HiOutlineRocketLaunch } from 'react-icons/hi2'
import { useApp } from '../context/AppContext'

const SKILL_SUGGESTIONS = [
  'Python', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'SQL', 'Git',
  'Docker', 'AWS', 'Machine Learning', 'Data Analysis', 'HTML/CSS',
  'Java', 'C++', 'Go', 'Rust', 'PostgreSQL', 'MongoDB', 'REST APIs',
  'GraphQL', 'Kubernetes', 'Linux', 'TensorFlow', 'PyTorch', 'Pandas',
]

const INTEREST_SUGGESTIONS = [
  'Artificial Intelligence', 'Machine Learning', 'Web Development', 'Data Science',
  'Cloud Computing', 'Cybersecurity', 'Mobile Development', 'DevOps',
  'Blockchain', 'Game Development', 'UX Design', 'Backend Development',
  'Frontend Development', 'Full Stack', 'Natural Language Processing',
]

const CAREER_GOALS = [
  'ML Engineer', 'Data Scientist', 'Full Stack Developer', 'Backend Developer',
  'Frontend Developer', 'DevOps Engineer', 'Cloud Architect', 'Data Engineer',
  'AI Research Scientist', 'Software Engineer', 'Site Reliability Engineer',
  'Product Manager', 'Security Engineer', 'Mobile Developer',
]

function TagInput({ label, suggestions, value, onChange, placeholder }) {
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
      <label className="block text-sm font-medium">{label}</label>
      <div className="input-field flex flex-wrap gap-2 min-h-[48px] !py-2 focus-within:ring-2 focus-within:ring-primary-500">
        {value.map((tag) => (
          <span key={tag} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-sm font-medium">
            {tag}
            <button type="button" onClick={() => removeTag(tag)} className="hover:text-red-500 ml-0.5">&times;</button>
          </span>
        ))}
        <input
          type="text"
          value={input}
          onChange={(e) => { setInput(e.target.value); setShowSuggestions(true) }}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
          onKeyDown={handleKeyDown}
          placeholder={value.length ? '' : placeholder}
          className="flex-1 min-w-[120px] bg-transparent outline-none text-sm"
        />
      </div>
      {showSuggestions && filtered.length > 0 && (
        <div className="relative z-10">
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
    </div>
  )
}

export default function Profile() {
  const { student, saveStudent, buildRoadmap } = useApp()
  const navigate = useNavigate()
  const [saving, setSaving] = useState(false)

  const { register, handleSubmit, reset, watch, setValue, trigger, getValues, formState: { errors } } = useForm({
    defaultValues: {
      name: '', current_skills: [], interests: [], career_goal: '',
      skill_level: 'beginner', learning_style: '', hours_per_week: 10,
    },
  })

  useEffect(() => {
    if (student) {
      reset({
        name: student.name || '',
        current_skills: student.current_skills || [],
        interests: student.interests || [],
        career_goal: student.career_goal || '',
        skill_level: (student.skill_level || 'beginner').toLowerCase(),
        learning_style: student.learning_style || '',
        hours_per_week: student.hours_per_week || 10,
      })
    }
  }, [student, reset])

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
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl sm:text-3xl font-display font-bold mb-2">
          {student ? 'Edit Profile' : 'Create Your Profile'}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8">
          Tell us about yourself so we can personalise your learning experience.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Name */}
          <div className="glass-card p-6 space-y-5">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 font-bold text-sm">1</div>
              Basic Information
            </h2>

            <div>
              <label className="block text-sm font-medium mb-1">Full Name *</label>
              <input {...register('name', { required: 'Name is required' })} className="input-field" placeholder="Alice Johnson" />
              {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Career Goal *</label>
              <input
                {...register('career_goal', { required: 'Career goal is required' })}
                className="input-field" placeholder="e.g. ML Engineer" list="career-goals"
              />
              <datalist id="career-goals">
                {CAREER_GOALS.map((g) => <option key={g} value={g} />)}
              </datalist>
              {errors.career_goal && <p className="text-red-500 text-xs mt-1">{errors.career_goal.message}</p>}
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Skill Level</label>
                <select {...register('skill_level')} className="input-field">
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Learning Style</label>
                <select {...register('learning_style')} className="input-field">
                  <option value="">Select...</option>
                  <option value="visual">Visual</option>
                  <option value="auditory">Auditory</option>
                  <option value="reading">Reading/Writing</option>
                  <option value="kinesthetic">Hands-on</option>
                </select>
              </div>
            </div>
          </div>

          {/* Skills & Interests */}
          <div className="glass-card p-6 space-y-5">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-accent-100 dark:bg-accent-900/30 flex items-center justify-center text-accent-600 font-bold text-sm">2</div>
              Skills & Interests
            </h2>

            <TagInput
              label="Current Skills"
              suggestions={SKILL_SUGGESTIONS}
              value={watch('current_skills') || []}
              onChange={(v) => setValue('current_skills', v)}
              placeholder="Type or select skills..."
            />

            <TagInput
              label="Interests"
              suggestions={INTEREST_SUGGESTIONS}
              value={watch('interests') || []}
              onChange={(v) => setValue('interests', v)}
              placeholder="Type or select interests..."
            />
          </div>

          {/* Weekly hours */}
          <div className="glass-card p-6">
            <label className="block text-sm font-medium mb-2">Hours per week</label>
            <div className="flex items-center gap-4">
              <input
                type="range" min="1" max="40" step="1"
                {...register('hours_per_week', { valueAsNumber: true })}
                className="flex-1 accent-primary-600"
              />
              <span className="w-12 text-center font-semibold text-lg">{watch('hours_per_week')}h</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3">
            <button type="submit" disabled={saving} className="btn-primary flex items-center justify-center gap-2">
              {saving ? <HiOutlineArrowPath className="w-5 h-5 animate-spin" /> : <HiOutlineCheckCircle className="w-5 h-5" />}
              Save Profile
            </button>
            <button type="button" onClick={() => reset()} className="btn-ghost">Reset</button>
            <button type="button" onClick={onGenerateRoadmap} disabled={saving} className="btn-secondary flex items-center justify-center gap-2 ml-auto">
              <HiOutlineRocketLaunch className="w-5 h-5" /> Generate Roadmap
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}
