import api from './api'

/* ── Study Planner ───────────────────────────────────────── */

// Sessions
export const getStudySessions = (userId, params = {}) =>
  api.get('/api/study-planner', { params: { user_id: userId, ...params } })

export const createStudySession = (userId, data) =>
  api.post('/api/study-planner', data, { params: { user_id: userId } })

export const updateStudySession = (userId, sessionId, data) =>
  api.put(`/api/study-planner/${sessionId}`, data, { params: { user_id: userId } })

export const deleteStudySession = (userId, sessionId) =>
  api.delete(`/api/study-planner/${sessionId}`, { params: { user_id: userId } })

export const completeStudySession = (userId, sessionId) =>
  api.post(`/api/study-planner/${sessionId}/complete`, null, { params: { user_id: userId } })

// Calendar
export const getStudyCalendar = (userId, params = {}) =>
  api.get('/api/study-planner/calendar', { params: { user_id: userId, ...params } })

// Analytics
export const getStudyAnalytics = (userId) =>
  api.get('/api/study-planner/analytics', { params: { user_id: userId } })

// Dashboard
export const getStudyDashboard = (userId) =>
  api.get('/api/study-planner/dashboard', { params: { user_id: userId } })

// Weekly planner
export const getStudyWeekly = (userId) =>
  api.get('/api/study-planner/weekly', { params: { user_id: userId } })

// Auto-generate from roadmap
export const generateStudySessions = (userId, data) =>
  api.post('/api/study-planner/generate', data, { params: { user_id: userId } })

// Goals
export const getStudyGoal = (userId) =>
  api.get('/api/study-planner/goal', { params: { user_id: userId } })

export const updateStudyGoal = (userId, data) =>
  api.put('/api/study-planner/goal', data, { params: { user_id: userId } })

// Streak
export const getStudyStreak = (userId) =>
  api.get('/api/study-planner/streak', { params: { user_id: userId } })

// AI
export const optimizeStudySchedule = (userId) =>
  api.post('/api/study-planner/optimize', null, { params: { user_id: userId } })

export const getDailyStudyTip = (userId) =>
  api.get('/api/study-planner/daily-tip', { params: { user_id: userId } })
