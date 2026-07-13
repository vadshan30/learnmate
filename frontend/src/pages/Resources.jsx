import { useEffect, useState, useMemo, useCallback, useRef } from 'react'
import { motion } from 'framer-motion'
import {
  HiOutlineMagnifyingGlass, HiOutlineBookOpen, HiOutlineBriefcase,
  HiOutlineAcademicCap, HiOutlineClock, HiOutlineFunnel,
} from 'react-icons/hi2'
import { useApp } from '../context/AppContext'
import { searchResources } from '../services/api'
import { SkeletonCard } from '../components/common/SkeletonLoader'
import EmptyState from '../components/common/EmptyState'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.05 } } }

const TABS = [
  { key: 'courses', label: 'Courses', icon: HiOutlineBookOpen },
  { key: 'projects', label: 'Projects', icon: HiOutlineBriefcase },
  { key: 'certifications', label: 'Certifications', icon: HiOutlineAcademicCap },
]

const LEVELS = ['All', 'Beginner', 'Intermediate', 'Advanced', 'Easy', 'Medium', 'Hard']

function ResourceCard({ item, type }) {
  const skills = item.skills_gained || item.required_skills || item.skills_covered || []
  const level = item.level || item.difficulty || ''
  const levelStr = typeof level === 'object' ? level.value || '' : level
  const provider = item.provider || item.domain || ''
  const duration = item.duration || item.estimated_hours || ''

  return (
    <motion.div variants={fadeUp} whileHover={{ y: -3 }} className="glass-card p-5 flex flex-col">
      <div className="flex items-start justify-between gap-2 mb-3">
        <span className={`badge ${levelStr.toLowerCase().includes('beginner') || levelStr.toLowerCase().includes('easy') ? 'badge-green' : levelStr.toLowerCase().includes('intermediate') || levelStr.toLowerCase().includes('medium') ? 'badge-yellow' : 'badge-purple'}`}>
          {levelStr || type}
        </span>
        {provider && <span className="text-xs text-gray-400">{provider}</span>}
      </div>
      <h3 className="font-semibold mb-2 line-clamp-2">{item.title || item.name}</h3>
      {item.description && <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">{item.description}</p>}
      <div className="mt-auto">
        {skills.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {skills.slice(0, 4).map((s, i) => <span key={i} className="text-[11px] px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">{s}</span>)}
            {skills.length > 4 && <span className="text-[11px] px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-400">+{skills.length - 4}</span>}
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default function Resources() {
  const { courses, projects, certifications, fetchCatalog, loading } = useApp()
  const [tab, setTab] = useState('courses')
  const [search, setSearch] = useState('')
  const [levelFilter, setLevelFilter] = useState('All')
  const [serverResults, setServerResults] = useState(null)
  const [searching, setSearching] = useState(false)
  const debounceRef = useRef(null)

  useEffect(() => { fetchCatalog() }, [fetchCatalog])

  const doSearch = useCallback(async (q) => {
    if (!q.trim()) { setServerResults(null); return }
    setSearching(true)
    try {
      const res = await searchResources({ q, top_k: 20 })
      setServerResults(res.data?.data || [])
    } catch {
      setServerResults([])
    } finally {
      setSearching(false)
    }
  }, [])

  useEffect(() => {
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => doSearch(search), 350)
    return () => clearTimeout(debounceRef.current)
  }, [search, doSearch])

  const catalogItems = tab === 'courses' ? courses : tab === 'projects' ? projects : certifications

  const filtered = useMemo(() => {
    let list = (search.trim() && serverResults !== null ? serverResults : catalogItems) || []
    if (levelFilter !== 'All') {
      list = list.filter((item) => {
        const level = String(item.level || item.difficulty || '').toLowerCase()
        return level.includes(levelFilter.toLowerCase())
      })
    }
    return list
  }, [catalogItems, serverResults, search, levelFilter])

  return (
    <div className="page-container">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        <motion.div variants={fadeUp}>
          <h1 className="text-2xl sm:text-3xl font-display font-bold mb-2">Learning Resources</h1>
          <p className="text-gray-500 dark:text-gray-400 mb-6">Browse courses, projects, and certifications</p>
        </motion.div>

        {/* Tabs */}
        <motion.div variants={fadeUp} className="flex gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-xl mb-6 w-fit">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                tab === t.key ? 'bg-white dark:bg-gray-700 shadow-sm text-primary-600' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <t.icon className="w-4 h-4" />
              {t.label}
            </button>
          ))}
        </motion.div>

        {/* Filters */}
        <motion.div variants={fadeUp} className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="relative flex-1 max-w-md">
            <HiOutlineMagnifyingGlass className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by title, description, or skill..."
              className="input-field !pl-10"
            />
          </div>
          <div className="flex items-center gap-2">
            <HiOutlineFunnel className="w-4 h-4 text-gray-400" />
            <select value={levelFilter} onChange={(e) => setLevelFilter(e.target.value)} className="input-field !w-auto">
              {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
        </motion.div>

        {/* Results */}
        {loading.student || searching ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => <SkeletonCard key={i} />)}
          </div>
        ) : filtered.length > 0 ? (
          <motion.div variants={stagger} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((item, i) => <ResourceCard key={item.id || i} item={item} type={tab} />)}
          </motion.div>
        ) : (
          <EmptyState
            icon={HiOutlineBookOpen}
            title={`No ${tab} found`}
            description={search ? 'Try a different search term or filter.' : `No ${tab} available yet.`}
          />
        )}
      </motion.div>
    </div>
  )
}
