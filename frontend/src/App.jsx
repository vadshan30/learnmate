import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom'
import Layout from './components/layout/Layout'
import GuestBanner from './components/common/GuestBanner'
import LoadingSpinner from './components/common/LoadingSpinner'
import ErrorBoundary from './components/common/ErrorBoundary'
import { useAuth } from './context/AuthContext'
import { useGuest } from './context/GuestContext'

const LandingPage = lazy(() => import('./pages/LandingPage'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'))
const ResetPassword = lazy(() => import('./pages/ResetPassword'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Profile = lazy(() => import('./pages/Profile'))
const Roadmap = lazy(() => import('./pages/Roadmap'))
const Resources = lazy(() => import('./pages/Resources'))
const Progress = lazy(() => import('./pages/Progress'))
const Settings = lazy(() => import('./pages/Settings'))
const StudyPlanner = lazy(() => import('./pages/StudyPlanner'))
const CareerTest = lazy(() => import('./pages/CareerTest'))
const NotFound = lazy(() => import('./pages/NotFound'))

function ProtectedRoute() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const { isGuest, initialized: guestReady } = useGuest()

  if (authLoading || !guestReady) {
    return (
      <div className="flex items-center justify-center h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!isAuthenticated && !isGuest) return <Navigate to="/login" replace />
  return <Outlet />
}

function PublicRoute() {
  const { isAuthenticated, loading } = useAuth()
  const { isGuest, initialized: guestReady } = useGuest()
  const location = useLocation()

  if (loading || !guestReady) {
    return (
      <div className="flex items-center justify-center h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (isAuthenticated) return <Navigate to="/dashboard" replace />

  if (isGuest && location.pathname === '/') return <Navigate to="/dashboard" replace />

  return <Outlet />
}

function GuestBannerWrapper() {
  return (
    <>
      <GuestBanner />
      <Outlet />
    </>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<div className="flex items-center justify-center h-screen"><LoadingSpinner size="lg" /></div>}>
        <Routes>
          {/* Public-only routes (redirect to dashboard if logged in or guest) */}
          <Route element={<PublicRoute />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
          </Route>

          {/* Protected routes (auth or guest allowed) */}
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route element={<GuestBannerWrapper />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/roadmap" element={<Roadmap />} />
                <Route path="/resources" element={<Resources />} />
                <Route path="/progress" element={<Progress />} />
                <Route path="/study-planner" element={<StudyPlanner />} />
                <Route path="/career-test" element={<CareerTest />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/settings" element={<Settings />} />
              </Route>
            </Route>
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}
