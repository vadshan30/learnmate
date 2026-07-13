export const slugify = (str) =>
  str.toLowerCase().trim().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')

export const truncate = (str, n = 100) =>
  str && str.length > n ? str.slice(0, n) + '...' : str

export const formatDate = (d) =>
  d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : ''

export const formatNumber = (n) =>
  n >= 1000 ? (n / 1000).toFixed(1) + 'k' : String(n)

export const skillLevelColor = (level) => {
  const l = (level || '').toLowerCase()
  if (l === 'beginner') return 'badge-green'
  if (l === 'intermediate') return 'badge-blue'
  if (l === 'advanced') return 'badge-purple'
  return 'badge-yellow'
}

export const difficultyColor = (d) => {
  const l = (d || '').toLowerCase()
  if (l === 'easy' || l === 'beginner') return 'badge-green'
  if (l === 'medium' || l === 'intermediate') return 'badge-yellow'
  if (l === 'hard' || l === 'advanced') return 'badge-red'
  return 'badge-blue'
}
