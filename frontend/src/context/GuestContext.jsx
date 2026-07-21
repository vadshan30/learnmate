import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react'

const GuestContext = createContext(null)

const GUEST_KEY = 'learnmate_guest'
const GUEST_ID_KEY = 'learnmate_guest_id'

function generateGuestId() {
  return 'guest_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36)
}

function loadGuestData() {
  try {
    const raw = localStorage.getItem(GUEST_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function saveGuestData(data) {
  localStorage.setItem(GUEST_KEY, JSON.stringify(data))
}

export function GuestProvider({ children }) {
  const [isGuest, setIsGuest] = useState(false)
  const [guestData, setGuestData] = useState(null)
  const [initialized, setInitialized] = useState(false)

  useEffect(() => {
    const guestId = localStorage.getItem(GUEST_ID_KEY)
    if (guestId) {
      setIsGuest(true)
      setGuestData(loadGuestData() || {})
    }
    setInitialized(true)
  }, [])

  const enterGuestMode = useCallback(() => {
    let guestId = localStorage.getItem(GUEST_ID_KEY)
    if (!guestId) {
      guestId = generateGuestId()
      localStorage.setItem(GUEST_ID_KEY, guestId)
    }
    setIsGuest(true)
    const existing = loadGuestData() || {}
    setGuestData(existing)
    localStorage.setItem('learnmate_student_id', guestId)
  }, [])

  const exitGuestMode = useCallback(() => {
    setIsGuest(false)
    setGuestData(null)
    localStorage.removeItem(GUEST_ID_KEY)
    localStorage.removeItem(GUEST_KEY)
    localStorage.removeItem('learnmate_student_id')
  }, [])

  const updateGuestData = useCallback((key, value) => {
    setGuestData((prev) => {
      const updated = { ...(prev || {}), [key]: value }
      saveGuestData(updated)
      return updated
    })
  }, [])

  const getGuestDataForMigration = useCallback(() => {
    if (!guestData) return {}
    const migration = {}
    if (guestData.profile) migration.profile = guestData.profile
    if (guestData.roadmap) migration.roadmap = guestData.roadmap
    if (guestData.progress) migration.progress = guestData.progress
    if (guestData.studySessions) migration.study_sessions = guestData.studySessions
    if (guestData.studyGoal) migration.study_goal = guestData.studyGoal
    return migration
  }, [guestData])

  const hasGuestData = useCallback(() => {
    if (!guestData) return false
    return !!(
      guestData.profile ||
      guestData.roadmap ||
      guestData.progress ||
      guestData.studySessions?.length ||
      guestData.studyGoal
    )
  }, [guestData])

  const value = useMemo(() => ({
    isGuest,
    guestData,
    initialized,
    enterGuestMode,
    exitGuestMode,
    updateGuestData,
    getGuestDataForMigration,
    hasGuestData,
  }), [isGuest, guestData, initialized, enterGuestMode, exitGuestMode, updateGuestData, getGuestDataForMigration, hasGuestData])

  return <GuestContext.Provider value={value}>{children}</GuestContext.Provider>
}

export const useGuest = () => {
  const ctx = useContext(GuestContext)
  if (!ctx) throw new Error('useGuest must be used within GuestProvider')
  return ctx
}
