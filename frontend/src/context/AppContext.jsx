import { createContext, useContext, useEffect, useState, useCallback, useRef, useMemo } from 'react'
import toast from 'react-hot-toast'
import * as api from '../services/api'
import * as studyApi from '../services/studyPlannerApi'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [student, setStudent] = useState(null)
  const [roadmap, setRoadmap] = useState(null)
  const [progress, setProgress] = useState(null)
  const [courses, setCourses] = useState([])
  const [projects, setProjects] = useState([])
  const [certifications, setCertifications] = useState([])
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState({})
  const [initialized, setInitialized] = useState(false)
  const [studySessions, setStudySessions] = useState([])
  const [studyGoal, setStudyGoal] = useState(null)
  const [studyAnalytics, setStudyAnalytics] = useState(null)
  const [studyDashboard, setStudyDashboard] = useState(null)
  const [careerTestResult, setCareerTestResult] = useState(null)
  const [careerTestHistory, setCareerTestHistory] = useState([])
  const studentIdRef = useRef(null)

  const wrap = useCallback(async (key, fn) => {
    setLoading((p) => ({ ...p, [key]: true }))
    try {
      return await fn()
    } finally {
      setLoading((p) => ({ ...p, [key]: false }))
    }
  }, [])

  // Load student data for a given student_id (typically = user.id when authenticated)
  const loadStudentData = useCallback(async (sid) => {
    if (!sid) return
    studentIdRef.current = sid
    localStorage.setItem('learnmate_student_id', sid)
    try {
      const r = await api.getStudent(sid)
      setStudent(r.data)

      const [roadmapRes, progressRes] = await Promise.allSettled([
        api.getRoadmap(sid),
        api.getProgress(sid),
      ])

      if (roadmapRes.status === 'fulfilled') {
        setRoadmap(roadmapRes.value.data?.roadmap || roadmapRes.value.data)
      }
      if (progressRes.status === 'fulfilled') {
        setProgress(progressRes.value.data?.data || null)
      }
    } catch {
      // Student profile may not exist yet (newly registered user)
      setStudent(null)
    }
  }, [])

  // Initialize: try to load student from stored student_id
  useEffect(() => {
    const id = localStorage.getItem('learnmate_student_id')
    if (id) {
      wrap('init', async () => {
        await loadStudentData(id)
        setInitialized(true)
      })
    } else {
      setInitialized(true)
    }
    api.getHealth().then((r) => setHealth(r.data)).catch(() => {})
    fetchCatalog()
  }, [wrap, loadStudentData])

  // Called by AuthContext after login/register — loads or creates student profile
  const initStudentForUser = useCallback(async (userId, userName) => {
    studentIdRef.current = userId
    localStorage.setItem('learnmate_student_id', userId)
    try {
      const r = await api.getStudent(userId)
      setStudent(r.data)
    } catch {
      // Auto-create student profile for new user
      try {
        const r = await api.createStudent({ name: userName || 'Student' })
        const profile = r.data?.data || r.data
        setStudent(profile)
      } catch {
        setStudent(null)
      }
    }
  }, [])

  const clearStudentData = useCallback(() => {
    setStudent(null)
    setRoadmap(null)
    setProgress(null)
    setStudySessions([])
    setStudyGoal(null)
    setStudyAnalytics(null)
    setStudyDashboard(null)
    studentIdRef.current = null
    localStorage.removeItem('learnmate_student_id')
  }, [])

  const saveStudent = useCallback(async (data) => {
    const result = await wrap('saveStudent', async () => {
      const payload = {
        name: data.name || '',
        email: data.email || null,
        career_goal: data.career_goal || '',
        skill_level: data.skill_level || 'beginner',
        learning_style: data.learning_style || null,
        hours_per_week: data.hours_per_week || null,
        preferred_study_time: data.preferred_study_time || null,
        preferred_job_role: data.preferred_job_role || null,
        dream_company: data.dream_company || null,
        experience_level: data.experience_level || null,
        github_url: data.github_url || null,
        linkedin_url: data.linkedin_url || null,
        current_skills: data.current_skills || [],
        interests: data.interests || [],
        current_goals: data.current_goals || [],
        completed_topics: data.completed_topics || [],
      }

      let lastError = null
      for (let attempt = 1; attempt <= 3; attempt++) {
        try {
          if (student?.student_id) return await api.updateStudent(student.student_id, payload)
          return await api.createStudent(payload)
        } catch (err) {
          lastError = err
          if (attempt < 3) {
            const delayMs = attempt * 500
            await new Promise((resolve) => setTimeout(resolve, delayMs))
          }
        }
      }
      throw lastError
    })
    const profile = result.data?.data || result.data
    setStudent(profile)
    if (profile?.student_id) localStorage.setItem('learnmate_student_id', profile.student_id)
    return profile
  }, [student, wrap])

  const removeStudent = useCallback(async () => {
    if (!student?.student_id) return
    await wrap('delete', () => api.deleteStudent(student.student_id))
    clearStudentData()
  }, [student, wrap, clearStudentData])

  const fetchRoadmap = useCallback(async () => {
    if (!student?.student_id) return
    try {
      const r = await wrap('roadmap', () => api.getRoadmap(student.student_id))
      setRoadmap(r.data?.roadmap || r.data)
    } catch {
      setRoadmap(null)
    }
  }, [student, wrap])

  const fetchProgress = useCallback(async () => {
    if (!student?.student_id) return
    try {
      const r = await api.getProgress(student.student_id)
      setProgress(r.data?.data || null)
    } catch {
      setProgress(null)
    }
  }, [student])

  const buildRoadmap = useCallback(async (opts = {}) => {
    if (!student?.student_id) throw new Error('Create a profile first')
    const r = await wrap('roadmap', () =>
      api.generateRoadmap({ student_id: student.student_id, weeks: opts.weeks || 12, hours_per_week: opts.hours_per_week || 10 })
    )
    setRoadmap(r.data?.roadmap || r.data)
    setTimeout(() => fetchProgress(), 500)
    return r.data
  }, [student, wrap, fetchProgress])

  const completeTopic = useCallback(async (topicName, completed = true) => {
    if (!student?.student_id) { toast.error('Create a profile first'); return }
    setLoading((p) => ({ ...p, topic: true }))
    try {
      const r = await api.completeTopic({
        student_id: student.student_id,
        topic_name: topicName,
        completed,
      })
      setProgress(r.data?.data || null)
      await fetchRoadmap()
      return r.data
    } catch (e) {
      const msg = e?.response?.data?.message || e?.message || 'Failed to update topic'
      toast.error(msg)
      throw e
    } finally {
      setLoading((p) => ({ ...p, topic: false }))
    }
  }, [student, fetchRoadmap])

  const fetchCatalog = useCallback(async () => {
    const [c, p, cert] = await Promise.allSettled([api.getCourses(), api.getProjects(), api.getCertifications()])
    if (c.status === 'fulfilled') setCourses(c.value.data)
    if (p.status === 'fulfilled') setProjects(p.value.data)
    if (cert.status === 'fulfilled') setCertifications(cert.value.data)
  }, [])

  // ── Study Planner ────────────────────────────────────────────────────

  const fetchStudySessions = useCallback(async () => {
    if (!student?.student_id) return
    try {
      const r = await studyApi.getStudySessions(student.student_id)
      setStudySessions(r.data?.data || [])
    } catch {
      setStudySessions([])
    }
  }, [student])

  const fetchStudyGoal = useCallback(async () => {
    if (!student?.student_id) return
    try {
      const r = await studyApi.getStudyGoal(student.student_id)
      setStudyGoal(r.data?.data || null)
    } catch {
      setStudyGoal(null)
    }
  }, [student])

  const fetchStudyAnalytics = useCallback(async () => {
    if (!student?.student_id) return
    try {
      const r = await studyApi.getStudyAnalytics(student.student_id)
      setStudyAnalytics(r.data?.data || null)
    } catch {
      setStudyAnalytics(null)
    }
  }, [student])

  const fetchStudyDashboard = useCallback(async () => {
    if (!student?.student_id) return
    try {
      const r = await studyApi.getStudyDashboard(student.student_id)
      setStudyDashboard(r.data?.data || null)
    } catch {
      setStudyDashboard(null)
    }
  }, [student])

  const createStudySession = useCallback(async (data) => {
    if (!student?.student_id) { toast.error('Create a profile first'); return }
    try {
      const r = await studyApi.createStudySession(student.student_id, data)
      setStudySessions((prev) => [...prev, r.data?.data])
      toast.success('Session created')
      return r.data?.data
    } catch (e) {
      toast.error(e?.message || 'Failed to create session')
      throw e
    }
  }, [student])

  const updateStudySession = useCallback(async (sessionId, data) => {
    if (!student?.student_id) return
    try {
      const r = await studyApi.updateStudySession(student.student_id, sessionId, data)
      setStudySessions((prev) => prev.map((s) => s.id === sessionId ? r.data?.data : s))
      return r.data?.data
    } catch (e) {
      toast.error(e?.message || 'Failed to update session')
      throw e
    }
  }, [student])

  const deleteStudySession = useCallback(async (sessionId) => {
    if (!student?.student_id) return
    try {
      await studyApi.deleteStudySession(student.student_id, sessionId)
      setStudySessions((prev) => prev.filter((s) => s.id !== sessionId))
      toast.success('Session deleted')
    } catch (e) {
      toast.error(e?.message || 'Failed to delete session')
      throw e
    }
  }, [student])

  const completeStudySession = useCallback(async (sessionId) => {
    if (!student?.student_id) return
    try {
      const r = await studyApi.completeStudySession(student.student_id, sessionId)
      setStudySessions((prev) => prev.map((s) => s.id === sessionId ? r.data?.data : s))
      toast.success('Session completed!')
      return r.data?.data
    } catch (e) {
      toast.error(e?.message || 'Failed to complete session')
      throw e
    }
  }, [student])

  const saveStudyGoal = useCallback(async (data) => {
    if (!student?.student_id) return
    try {
      const r = await studyApi.updateStudyGoal(student.student_id, data)
      setStudyGoal(r.data?.data)
      toast.success('Goal updated')
      return r.data?.data
    } catch (e) {
      toast.error(e?.message || 'Failed to update goal')
      throw e
    }
  }, [student])

  const generateSessionsFromRoadmap = useCallback(async (data) => {
    if (!student?.student_id) { toast.error('Create a profile first'); return }
    try {
      const r = await studyApi.generateStudySessions(student.student_id, data)
      const newSessions = r.data?.data || []
      setStudySessions((prev) => [...prev, ...newSessions])
      toast.success(`Generated ${newSessions.length} sessions`)
      return newSessions
    } catch (e) {
      toast.error(e?.message || 'Failed to generate sessions')
      throw e
    }
  }, [student])

  const fetchAllStudyData = useCallback(async () => {
    if (!student?.student_id) return
    await Promise.allSettled([
      fetchStudySessions(),
      fetchStudyGoal(),
      fetchStudyAnalytics(),
      fetchStudyDashboard(),
    ])
  }, [student, fetchStudySessions, fetchStudyGoal, fetchStudyAnalytics, fetchStudyDashboard])

  // ── Career Test ──────────────────────────────────────────────────────

  const fetchCareerTestHistory = useCallback(async () => {
    const userId = student?.student_id || localStorage.getItem('learnmate_guest_id') || 'guest'
    try {
      const r = await api.getCareerTestHistory(userId)
      const history = r.data?.data || []
      setCareerTestHistory(history)
      if (history.length > 0) setCareerTestResult(history[0])
      return history
    } catch {
      setCareerTestHistory([])
      setCareerTestResult(null)
      return []
    }
  }, [student])

  const value = useMemo(() => ({
    student, setStudent, saveStudent, removeStudent,
    roadmap, setRoadmap, fetchRoadmap, buildRoadmap,
    progress, fetchProgress, completeTopic,
    courses, projects, certifications, fetchCatalog,
    health, loading, initialized,
    initStudentForUser, clearStudentData,
    studySessions, setStudySessions, fetchStudySessions,
    studyGoal, setStudyGoal, fetchStudyGoal, saveStudyGoal,
    studyAnalytics, setStudyAnalytics, fetchStudyAnalytics,
    studyDashboard, setStudyDashboard, fetchStudyDashboard,
    createStudySession, updateStudySession, deleteStudySession, completeStudySession,
    generateSessionsFromRoadmap, fetchAllStudyData,
    careerTestResult, setCareerTestResult, careerTestHistory, setCareerTestHistory, fetchCareerTestHistory,
  }), [
    student, loading, initialized,
    roadmap, progress, courses, projects, certifications, health,
    studySessions, studyGoal, studyAnalytics, studyDashboard,
    careerTestResult, careerTestHistory,
    saveStudent, removeStudent, fetchRoadmap, buildRoadmap, fetchProgress, completeTopic,
    fetchCatalog, initStudentForUser, clearStudentData,
    fetchStudySessions, fetchStudyGoal, saveStudyGoal, fetchStudyAnalytics, fetchStudyDashboard,
    createStudySession, updateStudySession, deleteStudySession, completeStudySession,
    generateSessionsFromRoadmap, fetchAllStudyData, fetchCareerTestHistory,
  ])

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export const useApp = () => {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}
