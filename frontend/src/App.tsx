import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

// 🔥 DEMO MODE - Set to true to bypass login
const DEMO_MODE = true

// Layout
import DashboardLayout from '@/components/layout/DashboardLayout'

// Auth Pages
import Login from '@/pages/auth/Login'
import Register from '@/pages/auth/Register'
import ForgotPassword from '@/pages/auth/ForgotPassword'

// Dashboard Pages
import Dashboard from '@/pages/dashboard/Dashboard'
import Analytics from '@/pages/dashboard/Analytics'

// Pages Management
import PagesList from '@/pages/pages/PagesList'
import ConnectPage from '@/pages/pages/ConnectPage'

// Comments
import CommentsList from '@/pages/comments/CommentsList'

// Settings
import Settings from '@/pages/settings/Settings'
import AIPrompts from '@/pages/settings/AIPrompts'
import ReplyRules from '@/pages/settings/ReplyRules'

// Billing
import Plans from '@/pages/billing/Plans'
import Subscription from '@/pages/billing/Subscription'

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore()

  // 🔥 Demo mode bypass
  if (DEMO_MODE) {
    return <>{children}</>
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Public Route Component (redirect if authenticated)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />
      <Route
        path="/forgot-password"
        element={
          <PublicRoute>
            <ForgotPassword />
          </PublicRoute>
        }
      />

      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="pages" element={<PagesList />} />
        <Route path="pages/connect" element={<ConnectPage />} />
        <Route path="comments" element={<CommentsList />} />
        <Route path="settings" element={<Settings />} />
        <Route path="settings/prompts" element={<AIPrompts />} />
        <Route path="settings/rules" element={<ReplyRules />} />
        <Route path="billing" element={<Plans />} />
        <Route path="billing/subscription" element={<Subscription />} />
      </Route>

      {/* 404 */}
      <Route
        path="*"
        element={
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-6xl font-bold text-gray-300">404</h1>
              <p className="mt-4 text-gray-600">Page not found</p>
              <a href="/" className="mt-4 inline-block btn-primary">
                Go Home
              </a>
            </div>
          </div>
        }
      />
    </Routes>
  )
}

export default App
