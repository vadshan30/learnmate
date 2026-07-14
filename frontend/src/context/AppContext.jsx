import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import toast from 'react-hot-toast'
import * as api from '../services/api'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [student, setStudent] = useState(null)
  const [roadmap, setRoadmap] = useState(null)
  const [progress, setProgress] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [courses, setCourses] = useState([])
  const [projects, setProjects] = useState([])
  const [certifications, setCertifications] = useState([])
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState({})

  const wrap = useCallback(async (key, fn) => {
    setLoading((p) => ({ ...p, [key]: true }))
    try {
      return await fn()
    } finally {
      setLoading((p) => ({ ...p, [key]: false }))
    }
  }, [])

  useEffect(() => {
    const id = localStorage.getItem('learnmate_student_id')
    if (id) {
      wrap('student', () => api.getStudent(id)).then((r) => setStudent(r.data)).catch(() => {
        localStorage.removeItem('learnmate_student_id')
      })
    }
    api.getHealth().then((r) => setHealth(r.data)).catch(() => {})
    // Load catalog data on mount so Dashboard/Progress have data
    fetchCatalog()
  }, [wrap])

  const saveStudent = useCallback(async (data) => {
    const result = await wrap('saveStudent', () => {
      if (student?.student_id) return api.updateStudent(student.student_id, data)
      return api.createStudent(data)
    })
    const profile = result.data?.data || result.data
    setStudent(profile)
    if (profile?.student_id) localStorage.setItem('learnmate_student_id', profile.student_id)
    toast.success('Profile saved!')
    return profile
  }, [student, wrap])

  const removeStudent = useCallback(async () => {
    if (!student?.student_id) return
    await wrap('delete', () => api.deleteStudent(student.student_id))
    setStudent(null)
    setRoadmap(null)
    setProgress(null)
    setChatMessages([])
    localStorage.removeItem('learnmate_student_id')
  }, [student, wrap])

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
    if (!student?.student_id) { toast.error('Create a profile first'); return }
    const r = await wrap('roadmap', () =>
      api.generateRoadmap({ student_id: student.student_id, weeks: opts.weeks || 12, hours_per_week: opts.hours_per_week || 10 })
    )
    setRoadmap(r.data?.roadmap || r.data)
    toast.success('Roadmap generated!')
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

  const sendMessage = useCallback(async (message) => {
    if (!student?.student_id) { toast.error('Create a profile first'); return }
    const userMsg = { role: 'user', content: message, ts: Date.now() }
    setChatMessages((p) => [...p, userMsg])
    setLoading((p) => ({ ...p, chat: true }))
    try {
      const r = await api.sendChat({ student_id: student.student_id, message })
      const assistantMsg = { role: 'assistant', content: r.data?.response || '', ts: Date.now() }
      setChatMessages((p) => [...p, assistantMsg])
      return r.data
    } catch (e) {
      setChatMessages((p) => [...p, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.', ts: Date.now() }])
      throw e
    } finally {
      setLoading((p) => ({ ...p, chat: false }))
    }
  }, [student])

  const clearMessages = useCallback(() => {
    setChatMessages([])
    if (student?.student_id) api.clearChat(student.student_id).catch(() => {})
  }, [student])

  const fetchChatHistory = useCallback(async () => {
    if (!student?.student_id) return
    try {
      const r = await api.getChatHistory(student.student_id)
      const messages = r.data?.data?.messages || []
      setChatMessages(messages.map((m, i) => ({ ...m, ts: Date.now() + i })))
    } catch {
      // History may not exist yet — that's fine
    }
  }, [student])

  const fetchCatalog = useCallback(async () => {
    const [c, p, cert] = await Promise.allSettled([api.getCourses(), api.getProjects(), api.getCertifications()])
    if (c.status === 'fulfilled') setCourses(c.value.data)
    if (p.status === 'fulfilled') setProjects(p.value.data)
    if (cert.status === 'fulfilled') setCertifications(cert.value.data)
  }, [])

  const value = {
    student, setStudent, saveStudent, removeStudent,
    roadmap, setRoadmap, fetchRoadmap, buildRoadmap,
    progress, fetchProgress, completeTopic,
    chatMessages, setChatMessages, sendMessage, clearMessages, fetchChatHistory,
    courses, projects, certifications, fetchCatalog,
    health, loading,
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export const useApp = () => {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}
