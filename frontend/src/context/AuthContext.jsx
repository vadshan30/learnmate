import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react'
import * as authApi from '../services/authApi'

const AuthContext = createContext(null)

const TOKEN_KEY = 'learnmate_access_token'
const REFRESH_KEY = 'learnmate_refresh_token'
const USER_KEY = 'learnmate_user'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [accessToken, setAccessToken] = useState(null)
  const [loading, setLoading] = useState(true)

  const getStorage = useCallback((remember) => {
    return remember !== false ? localStorage : sessionStorage
  }, [])

  const saveAuth = useCallback((tokenData, remember = true) => {
    const { access_token, refresh_token, user: userData } = tokenData
    setAccessToken(access_token)
    setUser(userData)
    const storage = getStorage(remember)
    storage.setItem(TOKEN_KEY, access_token)
    storage.setItem(REFRESH_KEY, refresh_token)
    storage.setItem(USER_KEY, JSON.stringify(userData))
  }, [getStorage])

  const clearAuth = useCallback(() => {
    setAccessToken(null)
    setUser(null)
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
    localStorage.removeItem(USER_KEY)
    sessionStorage.removeItem(TOKEN_KEY)
    sessionStorage.removeItem(REFRESH_KEY)
    sessionStorage.removeItem(USER_KEY)
    localStorage.removeItem('learnmate_student_id')
    sessionStorage.removeItem('learnmate_student_id')
  }, [])

  const register = useCallback(async (data) => {
    const res = await authApi.registerUser(data)
    return res.data
  }, [])

  const login = useCallback(async (data, remember = true) => {
    const res = await authApi.loginUser(data)
    saveAuth(res.data, remember)
    return res.data
  }, [saveAuth])

  const logout = useCallback(() => {
    clearAuth()
  }, [clearAuth])

  const migrateGuest = useCallback(async (guestData) => {
    if (!accessToken) return null
    const res = await authApi.migrateGuestData(guestData, accessToken)
    return res.data
  }, [accessToken])

  const refreshAccessToken = useCallback(async () => {
    const storedRefresh = localStorage.getItem(REFRESH_KEY) || sessionStorage.getItem(REFRESH_KEY)
    if (!storedRefresh) {
      clearAuth()
      return null
    }
    try {
      const res = await authApi.refreshToken(storedRefresh)
      saveAuth(res.data)
      return res.data.access_token
    } catch {
      clearAuth()
      return null
    }
  }, [saveAuth, clearAuth])

  // On mount: validate stored token
  useEffect(() => {
    const init = async () => {
      const storedToken = localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY)
      const storedUser = localStorage.getItem(USER_KEY) || sessionStorage.getItem(USER_KEY)

      if (!storedToken || !storedUser) {
        setLoading(false)
        return
      }

      try {
        const res = await authApi.getMe(storedToken)
        setUser(res.data)
        setAccessToken(storedToken)
      } catch {
        const newToken = await refreshAccessToken()
        if (!newToken) {
          clearAuth()
        }
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [refreshAccessToken, clearAuth])

  const value = useMemo(() => ({
    user,
    accessToken,
    loading,
    isAuthenticated: !!user && !!accessToken,
    register,
    login,
    logout,
    migrateGuest,
    refreshAccessToken,
  }), [user, accessToken, loading, register, login, logout, migrateGuest, refreshAccessToken])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
