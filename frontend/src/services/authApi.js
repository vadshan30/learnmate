import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const authApi = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

authApi.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred'
    return Promise.reject({ message: msg, status: error.response?.status })
  }
)

export const registerUser = (data) =>
  authApi.post('/api/auth/register', {
    full_name: data.full_name,
    username: data.username,
    email: data.email,
    password: data.password,
    confirm_password: data.confirm_password,
  })

export const loginUser = (data) =>
  authApi.post('/api/auth/login', {
    email_or_username: data.email_or_username,
    password: data.password,
  })

export const refreshToken = (token) =>
  authApi.post('/api/auth/refresh', { refresh_token: token })

export const getMe = (accessToken) =>
  authApi.get('/api/auth/me', {
    headers: { Authorization: `Bearer ${accessToken}` },
  })

export const forgotPassword = (email) =>
  authApi.post('/api/auth/forgot-password', { email })

export const resetPassword = (token, newPassword, confirmPassword) =>
  authApi.post('/api/auth/reset-password', {
    token,
    new_password: newPassword,
    confirm_password: confirmPassword,
  })

export const changePassword = (data, accessToken) =>
  authApi.post('/api/auth/change-password', {
    current_password: data.current_password,
    new_password: data.new_password,
    confirm_password: data.confirm_password,
  }, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })

export const migrateGuestData = (data, accessToken) =>
  authApi.post('/api/auth/migrate-guest', data, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })

export default authApi
