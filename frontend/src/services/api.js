import axios from 'axios'
import toast from 'react-hot-toast'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred'

    if (error.response?.status === 503) {
      toast.error('AI service is currently unavailable. Using offline mode.')
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Request timed out. Please try again.')
    } else if (!error.response) {
      toast.error('Backend is unreachable. Is the server running?')
    }

    return Promise.reject({ message: msg, status: error.response?.status, data: error.response?.data })
  }
)

/* ── Health ──────────────────────────────────────────────── */
export const getHealth = () => api.get('/health')

/* ── Students ────────────────────────────────────────────── */
export const getStudents = () => api.get('/api/student')
export const getStudent = (id) => api.get(`/api/student/${id}`)
export const createStudent = (data) => api.post('/api/student', data)
export const updateStudent = (id, data) => api.put(`/api/student/${id}`, data)
export const deleteStudent = (id) => api.delete(`/api/student/${id}`)
export const recordProgress = (id, params) =>
  api.post(`/api/student/${id}/progress`, null, { params })

/* ── Roadmap ─────────────────────────────────────────────── */
export const generateRoadmap = (data) => api.post('/api/roadmap', data)
export const getRoadmap = (id) => api.get(`/api/roadmap/${id}`)
export const updateRoadmap = (id, data) => api.put(`/api/roadmap/${id}`, data)
export const deleteRoadmap = (id) => api.delete(`/api/roadmap/${id}`)

/* ── Chat ────────────────────────────────────────────────── */
export const sendChat = (data) => api.post('/api/chat', data)
export const clearChat = (id) => api.delete(`/api/chat/${id}`)

/* ── Catalog ─────────────────────────────────────────────── */
export const getCourses = () => api.get('/api/courses')
export const getProjects = () => api.get('/api/projects')
export const getCertifications = () => api.get('/api/certifications')

/* ── Search ──────────────────────────────────────────────── */
export const searchResources = (params) => api.get('/api/search', { params })

export default api
