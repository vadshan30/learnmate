import { useEffect, useState, useMemo, useCallback, useRef } from 'react'
import { motion } from 'framer-motion'
import {
  HiOutlineMagnifyingGlass,
  HiOutlineBookOpen,
  HiOutlineBriefcase,
  HiOutlineAcademicCap,
  HiOutlineFunnel,
  HiOutlineArrowPath,
  HiOutlineExclamationTriangle,
  HiOutlineSquares2X2,
} from 'react-icons/hi2'
import {
  getResourceCourses,
  getResourceProjects,
  getResourceCertifications,
  searchAllResources,
} from '../services/api'
import { SkeletonCard } from '../components/common/SkeletonLoader'
import ResourceCard from '../components/common/ResourceCard'
import ProjectDetailsModal from '../components/project/ProjectDetailsModal'

const SORT_OPTIONS = [
  { key: 'default', label: 'Default' },
  { key: 'difficulty', label: 'Difficulty' },
  { key: 'duration', label: 'Duration' },
  { key: 'alpha', label: 'Alphabetical' },
]

const DIFFICULTY_ORDER = { beginner: 1, intermediate: 2, advanced: 3 }

function parseDurationWeeks(d) {
  const m = String(d || '').match(/(\d+)/)
  return m ? parseInt(m[1], 10) : 999
}

function sortItems(items, sortBy) {
  if (sortBy === 'default') return items
  const sorted = [...items]
  switch (sortBy) {
    case 'difficulty':
      return sorted.sort((a, b) => {
        const al = String(a.level || a.difficulty || '').toLowerCase()
        const bl = String(b.level || b.difficulty || '').toLowerCase()
        return (DIFFICULTY_ORDER[al] || 9) - (DIFFICULTY_ORDER[bl] || 9)
      })
    case 'duration':
      return sorted.sort((a, b) => parseDurationWeeks(a.duration || a.estimated_time) - parseDurationWeeks(b.duration || b.estimated_time))
    case 'alpha':
      return sorted.sort((a, b) => (a.title || a.name || '').localeCompare(b.title || b.name || ''))
    default:
      return sorted
  }
}

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

const stagger = {
  visible: { transition: { staggerChildren: 0.05 } },
}

const TABS = [
  { key: 'all', label: 'All', icon: HiOutlineSquares2X2 },
  { key: 'courses', label: 'Courses', icon: HiOutlineBookOpen },
  { key: 'projects', label: 'Projects', icon: HiOutlineBriefcase },
  { key: 'certifications', label: 'Certifications', icon: HiOutlineAcademicCap },
]

const LEVELS = ['All', 'Beginner', 'Intermediate', 'Advanced']
const DOMAINS = [
  'All',
  'Web Development',
  'Frontend Development',
  'Backend Development',
  'Full Stack Development',
  'Data Science',
  'Data Analytics',
  'Data Engineering',
  'Machine Learning',
  'Deep Learning',
  'Artificial Intelligence',
  'NLP',
  'Computer Vision',
  'Natural Language Processing',
  'Cloud Computing',
  'DevOps',
  'Cybersecurity',
  'Databases',
  'Database',
  'UI/UX',
  'Mobile Development',
  'Blockchain',
  'IoT',
  'Algorithmic Trading',
  'MLOps',
  'Architecture',
  'Automation',
  'RAG',
  'Generative AI',
  'Programming',
  'Networking',
  'Operating Systems',
  'Java Development',
  'Project Management',
]
const PROVIDERS = [
  'All',
  'LearnMate',
  'Coursera',
  'freeCodeCamp',
  'Great Learning',
  'Microsoft Learn',
  'IBM SkillsBuild',
  'Cisco Skills for All',
  'Hugging Face',
  'Google Cloud Skills Boost',
  'Google Developers',
  'Anthropic',
  'OpenAI',
  'Google',
  'Meta',
  'NVIDIA',
  'Amazon Web Services',
  'DeepLearning.AI',
  'Harvard University',
  'MathWorks',
  'edX',
  'KodeKloud',
  'Kubernetes',
  'Linux Journey',
  'MongoDB University',
  'Redis University',
  'Oracle',
  'Linux Foundation',
  'Databricks',
  'Snowflake',
  'HashiCorp',
  'Salesforce',
  'IBM',
  'Microsoft',
]

function getItemType(item) {
  if (item._type) return item._type
  if (item.exam_fee || item.validity || item.official_badge || item.career_roles) return 'certification'
  if (item.skills_covered || item.exam_link) return 'certification'
  if (item.estimated_time) return 'project'
  if (item.skills_gained || item.url) return 'course'
  return 'course'
}

export default function Resources() {
  const [courses, setCourses] = useState([])
  const [projects, setProjects] = useState([])
  const [certifications, setCertifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [tab, setTab] = useState('all')
  const [search, setSearch] = useState('')
  const [searchResults, setSearchResults] = useState(null)
  const [searching, setSearching] = useState(false)
  const [levelFilter, setLevelFilter] = useState('All')
  const [domainFilter, setDomainFilter] = useState('All')
  const [providerFilter, setProviderFilter] = useState('All')
  const [sortBy, setSortBy] = useState('default')
  const [selectedProject, setSelectedProject] = useState(null)
  const debounceRef = useRef(null)

  const fetchAllResources = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [cRes, pRes, certRes] = await Promise.allSettled([
        getResourceCourses(),
        getResourceProjects(),
        getResourceCertifications(),
      ])

      if (cRes.status === 'fulfilled') setCourses(cRes.value.data?.data || [])
      else console.error('Failed to fetch courses:', cRes.reason)

      if (pRes.status === 'fulfilled') setProjects(pRes.value.data?.data || [])
      else console.error('Failed to fetch projects:', pRes.reason)

      if (certRes.status === 'fulfilled') setCertifications(certRes.value.data?.data || [])
      else console.error('Failed to fetch certifications:', certRes.reason)

      const allFailed = [cRes, pRes, certRes].every((r) => r.status === 'rejected')
      if (allFailed) throw new Error('Failed to load resources from the server')
    } catch (e) {
      console.error('Resource fetch error:', e)
      setError(e.message || 'An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAllResources()
  }, [fetchAllResources])

  const doSearch = useCallback(async (q) => {
    if (!q.trim()) {
      setSearchResults(null)
      return
    }
    setSearching(true)
    try {
      const res = await searchAllResources({ q, top_k: 50 })
      const results = res.data?.data || []
      setSearchResults(
        results.map((item) => ({ ...item, _type: getItemType(item) }))
      )
    } catch (e) {
      console.error('Search error:', e)
      setSearchResults([])
    } finally {
      setSearching(false)
    }
  }, [])

  useEffect(() => {
    if (!search.trim()) {
      clearTimeout(debounceRef.current)
      setSearchResults(null)
      setSearching(false)
      return
    }
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => doSearch(search), 350)
    return () => clearTimeout(debounceRef.current)
  }, [search, doSearch])

  const handleTabChange = useCallback((newTab) => {
    setTab(newTab)
    setSearch('')
    setSearchResults(null)
    setLevelFilter('All')
    setDomainFilter('All')
    setProviderFilter('All')
    setSortBy('default')
    setSelectedProject(null)
  }, [])

  const handleClearFilters = useCallback(() => {
    setLevelFilter('All')
    setDomainFilter('All')
    setProviderFilter('All')
    setSearch('')
    setSearchResults(null)
  }, [])

  const allItems = useMemo(
    () => [
      ...courses.map((c) => ({ ...c, _type: 'course' })),
      ...projects.map((p) => ({ ...p, _type: 'project' })),
      ...certifications.map((c) => ({ ...c, _type: 'certification' })),
    ],
    [courses, projects, certifications]
  )

  const tabItems = useMemo(() => {
    if (searchResults !== null) return searchResults
    switch (tab) {
      case 'courses':
        return courses.map((c) => ({ ...c, _type: 'course' }))
      case 'projects':
        return projects.map((p) => ({ ...p, _type: 'project' }))
      case 'certifications':
        return certifications.map((c) => ({ ...c, _type: 'certification' }))
      default:
        return allItems
    }
  }, [tab, courses, projects, certifications, allItems, searchResults])

  const filtered = useMemo(() => {
    let list = tabItems

    if (levelFilter !== 'All') {
      list = list.filter((item) => {
        const level = (item.level || item.difficulty || '').toLowerCase()
        return level === levelFilter.toLowerCase()
      })
    }

    if (domainFilter !== 'All') {
      list = list.filter((item) => {
        const domain = (item.domain || item.category || '').toLowerCase()
        return domain === domainFilter.toLowerCase()
      })
    }

    if (providerFilter !== 'All') {
      list = list.filter((item) => {
        const provider = (item.provider || '').toLowerCase()
        return provider === providerFilter.toLowerCase()
      })
    }

    return sortItems(list, sortBy)
  }, [tabItems, levelFilter, domainFilter, providerFilter, sortBy])

  const hasActiveFilters =
    levelFilter !== 'All' || domainFilter !== 'All' || providerFilter !== 'All'

  const isInitialLoading = loading
  const isSearching = searching
  const hasError = error !== null
  const isEmpty = !isInitialLoading && !isSearching && filtered.length === 0

  return (
    <div className="page-container">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        {/* Header */}
        <motion.div variants={fadeUp} className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-display font-bold mb-2">
            Learning <span className="gradient-text">Resources</span>
          </h1>
          <p className="text-gray-500 dark:text-gray-400 text-base sm:text-lg">
            Discover {courses.length} courses, {projects.length} projects, and{' '}
            {certifications.length} certifications
          </p>
        </motion.div>

        {/* Tabs */}
        <motion.div
          variants={fadeUp}
          className="flex flex-wrap gap-1 p-1 bg-gray-100 dark:bg-gray-800/80 rounded-xl mb-6 w-fit"
        >
          {TABS.map((t) => {
            const count =
              t.key === 'all'
                ? courses.length + projects.length + certifications.length
                : t.key === 'courses'
                  ? courses.length
                  : t.key === 'projects'
                    ? projects.length
                    : certifications.length
            return (
              <button
                key={t.key}
                onClick={() => handleTabChange(t.key)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  tab === t.key
                    ? 'bg-white dark:bg-gray-700 shadow-sm text-primary-600 dark:text-primary-400'
                    : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                }`}
              >
                <t.icon className="w-4 h-4" />
                <span className="hidden sm:inline">{t.label}</span>
                <span
                  className={`text-xs px-1.5 py-0.5 rounded-full ${
                    tab === t.key
                      ? 'bg-primary-100 dark:bg-primary-900/50 text-primary-600 dark:text-primary-400'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
                  }`}
                >
                  {count}
                </span>
              </button>
            )
          })}
        </motion.div>

        {/* Search + Filters */}
        <motion.div variants={fadeUp} className="mb-6">
          <div className="flex flex-col sm:flex-row gap-3 mb-3">
            <div className="relative flex-1 max-w-lg">
              <HiOutlineMagnifyingGlass className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search courses, projects, or skills..."
                className="input-field !pl-11 !py-3"
              />
              {isSearching && (
                <div className="absolute right-3.5 top-1/2 -translate-y-1/2">
                  <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
              )}
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <HiOutlineFunnel className="w-4 h-4 text-gray-400 shrink-0" />
              <select
                value={levelFilter}
                onChange={(e) => setLevelFilter(e.target.value)}
                className="input-field !w-auto !py-2.5 text-sm"
              >
                {LEVELS.map((l) => (
                  <option key={l} value={l}>
                    {l === 'All' ? 'All Levels' : l}
                  </option>
                ))}
              </select>
              <select
                value={domainFilter}
                onChange={(e) => setDomainFilter(e.target.value)}
                className="input-field !w-auto !py-2.5 text-sm"
              >
                {DOMAINS.map((d) => (
                  <option key={d} value={d}>
                    {d === 'All' ? 'All Domains' : d}
                  </option>
                ))}
              </select>
              <select
                value={providerFilter}
                onChange={(e) => setProviderFilter(e.target.value)}
                className="input-field !w-auto !py-2.5 text-sm"
              >
                {PROVIDERS.map((p) => (
                  <option key={p} value={p}>
                    {p === 'All' ? 'All Providers' : p}
                  </option>
                ))}
              </select>
              {hasActiveFilters && (
                <button
                  onClick={handleClearFilters}
                  className="btn-ghost text-sm !px-3 !py-2"
                >
                  Clear
                </button>
              )}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="input-field !w-auto !py-2.5 text-sm"
              >
                {SORT_OPTIONS.map((s) => (
                  <option key={s.key} value={s.key}>
                    Sort: {s.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {!isInitialLoading && !isEmpty && (
            <p className="text-sm text-gray-400 dark:text-gray-500">
              Showing {filtered.length} of {tabItems.length} resources
            </p>
          )}
        </motion.div>

        {/* Content */}
        <motion.div variants={fadeUp}>
          {isInitialLoading ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : hasError ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-16 h-16 rounded-2xl bg-red-100 dark:bg-red-900/20 flex items-center justify-center mb-4">
                <HiOutlineExclamationTriangle className="w-8 h-8 text-red-500" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Something went wrong</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm max-w-sm mb-6">
                {error}
              </p>
              <button
                onClick={fetchAllResources}
                className="btn-primary flex items-center gap-2"
              >
                <HiOutlineArrowPath className="w-4 h-4" />
                Try Again
              </button>
            </div>
          ) : isEmpty ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-20 h-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-4">
                <HiOutlineMagnifyingGlass className="w-10 h-10 text-gray-300 dark:text-gray-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No resources found</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm max-w-sm mb-6">
                {search
                  ? `No results for "${search}". Try different keywords or clear your search.`
                  : 'No resources match your current filters. Try adjusting them.'}
              </p>
              <button onClick={handleClearFilters} className="btn-secondary text-sm">
                {search ? 'Clear Search' : 'Clear Filters'}
              </button>
            </div>
          ) : (
            <motion.div
              key={`${tab}-${search}-${levelFilter}-${domainFilter}-${providerFilter}`}
              variants={stagger}
              initial="hidden"
              animate="visible"
              className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5"
            >
              {filtered.map((item, i) => (
                <ResourceCard
                  key={item.id || i}
                  item={item}
                  type={getItemType(item)}
                  showType={tab === 'all' || searchResults !== null}
                  onViewDetails={(getItemType(item) === 'project') ? setSelectedProject : undefined}
                />
              ))}
            </motion.div>
          )}
        </motion.div>
      </motion.div>

      {/* Project Details Modal */}
      <ProjectDetailsModal
        project={selectedProject}
        isOpen={Boolean(selectedProject)}
        onClose={() => setSelectedProject(null)}
      />
    </div>
  )
}
