import React, { Suspense, lazy } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AuthProvider from './contexts/AuthProvider'
import ProtectedRoute from './components/ProtectedRoute'
import LoadingScreen from './components/LoadingScreen'
import { useAuth } from './store/useAuth'
import { RoleSelectPage, LoginPage, RegisterPage } from './features/auth'
import {
  TermsPage,
  PrivacyPage,
  HelpPage,
  NotFoundPage,
} from './features/public'
import { ProfilePage } from './features/public'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 5,
    },
  },
})

const HealthProfileOnboarding = lazy(() => import('./features/senior/HealthProfileOnboarding'))
const DailyRoutinePage = lazy(() => import('./features/senior/DailyRoutinePage'))
const HabitsPage = lazy(() => import('./features/senior/HabitsPage'))
const ProgressPage = lazy(() => import('./features/senior/ProgressPage'))
const CaregiverDashboard = lazy(() => import('./features/caregiver/CaregiverDashboard'))
const CaregiverAlertsPage = lazy(() => import('./features/caregiver/CaregiverAlertsPage'))
const CaregiverReportsPage = lazy(() => import('./features/caregiver/CaregiverReportsPage'))
const SeniorView = lazy(() => import('./features/caregiver/SeniorView'))
const AdminDashboard = lazy(() => import('./features/admin/AdminDashboard'))
const LandingPage = lazy(() => import('./features/public/LandingPage'))

function RoleRouter() {
  const { user, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!user) return <Navigate to="/" replace />
  if (user.role === 'senior') return <Navigate to="/routine" replace />
  if (user.role === 'caregiver') return <Navigate to="/caregiver" replace />
  if (user.role === 'admin') return <Navigate to="/admin" replace />
  return <Navigate to="/login" replace />
}

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<LoadingScreen />}>{children}</Suspense>
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public */}
          <Route path="/" element={<SuspenseWrapper><LandingPage /></SuspenseWrapper>} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/help" element={<HelpPage />} />

          {/* Profile (all roles) */}
          <Route path="/profile" element={
            <ProtectedRoute>
              <SuspenseWrapper><ProfilePage /></SuspenseWrapper>
            </ProtectedRoute>
          } />

          {/* Senior */}
          <Route path="/onboarding/health-profile" element={
            <ProtectedRoute useLayout={false}>
              <SuspenseWrapper><HealthProfileOnboarding /></SuspenseWrapper>
            </ProtectedRoute>
          } />
          <Route path="/routine" element={
            <ProtectedRoute requiredRole="senior">
              <SuspenseWrapper><DailyRoutinePage /></SuspenseWrapper>
            </ProtectedRoute>
          } />
          <Route path="/habits" element={
            <ProtectedRoute requiredRole="senior">
              <SuspenseWrapper><HabitsPage /></SuspenseWrapper>
            </ProtectedRoute>
          } />
          <Route path="/progress" element={
            <ProtectedRoute requiredRole="senior">
              <SuspenseWrapper><ProgressPage /></SuspenseWrapper>
            </ProtectedRoute>
          } />

          {/* Caregiver */}
          <Route path="/caregiver" element={
            <ProtectedRoute requiredRole="caregiver">
              <SuspenseWrapper><CaregiverDashboard /></SuspenseWrapper>
            </ProtectedRoute>
          } />
          <Route path="/caregiver/alerts" element={
            <ProtectedRoute requiredRole="caregiver">
              <SuspenseWrapper><CaregiverAlertsPage /></SuspenseWrapper>
            </ProtectedRoute>
          } />
          <Route path="/caregiver/reports" element={
            <ProtectedRoute requiredRole="caregiver">
              <SuspenseWrapper><CaregiverReportsPage /></SuspenseWrapper>
            </ProtectedRoute>
          } />
          <Route path="/caregiver/senior/:seniorId" element={
            <ProtectedRoute requiredRole="caregiver">
              <SuspenseWrapper><SeniorView /></SuspenseWrapper>
            </ProtectedRoute>
          } />

          {/* Admin */}
          <Route path="/admin" element={
            <ProtectedRoute requiredRole="admin">
              <SuspenseWrapper><AdminDashboard /></SuspenseWrapper>
            </ProtectedRoute>
          } />

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AuthProvider>
    </Router>
    </QueryClientProvider>
  )
}
