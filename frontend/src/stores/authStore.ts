/**
 * Authentication Store using Zustand
 * Created by: Karim (Frontend Lead)
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type {
  User,
  Organization,
  Subscription,
  AuthState,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  MeResponse,
} from '@/types/auth.types'
import { authService } from '@/services/auth.service'

interface AuthStore extends AuthState {
  // Actions
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  refreshTokens: () => Promise<void>
  fetchMe: () => Promise<void>
  setLoading: (loading: boolean) => void
  updateUser: (user: Partial<User>) => void
  updateOrganization: (org: Partial<Organization>) => void
}

// 🔥 DEMO MODE DATA
const DEMO_MODE = true
const DEMO_USER: User = {
  id: 'demo-user-id',
  email: 'demo@aiosol.com',
  first_name: 'রাফিক',
  last_name: 'আহমেদ',
  role: 'org_owner',
  is_active: true,
  is_verified: true,
  organization_id: 'demo-org-id',
  created_at: new Date().toISOString(),
}
const DEMO_ORG: Organization = {
  id: 'demo-org-id',
  name: 'Demo Business',
  slug: 'demo-business',
  settings: {
    timezone: 'Asia/Dhaka',
    language: 'bn',
    currency: 'BDT',
    reply_delay_min: 30,
    reply_delay_max: 120,
    auto_reply_enabled: true,
    ai_provider: 'openai',
    default_tone: 'professional',
  },
}
const DEMO_SUB: Subscription = {
  id: 'demo-sub-id',
  status: 'active',
  plan_name: 'Pro',
  replies_used: 234,
  replies_limit: 5000,
  pages_used: 2,
  pages_limit: 10,
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state (with demo data if DEMO_MODE)
      user: DEMO_MODE ? DEMO_USER : null,
      organization: DEMO_MODE ? DEMO_ORG : null,
      subscription: DEMO_MODE ? DEMO_SUB : null,
      accessToken: DEMO_MODE ? 'demo-token' : null,
      refreshToken: null,
      isAuthenticated: DEMO_MODE,
      isLoading: false,

      // Login
      login: async (data: LoginRequest) => {
        set({ isLoading: true })
        try {
          const response: TokenResponse = await authService.login(data)

          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
          })

          // Fetch user data
          await get().fetchMe()
        } finally {
          set({ isLoading: false })
        }
      },

      // Register
      register: async (data: RegisterRequest) => {
        set({ isLoading: true })
        try {
          const response: TokenResponse = await authService.register(data)

          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
          })

          // Fetch user data
          await get().fetchMe()
        } finally {
          set({ isLoading: false })
        }
      },

      // Logout
      logout: () => {
        set({
          user: null,
          organization: null,
          subscription: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        })
      },

      // Refresh tokens
      refreshTokens: async () => {
        const { refreshToken } = get()
        if (!refreshToken) {
          get().logout()
          return
        }

        try {
          const response: TokenResponse = await authService.refresh(refreshToken)

          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
          })
        } catch {
          get().logout()
        }
      },

      // Fetch current user
      fetchMe: async () => {
        const { accessToken } = get()
        if (!accessToken) {
          set({ isLoading: false })
          return
        }

        try {
          const response: MeResponse = await authService.me()

          set({
            user: response.user,
            organization: response.organization || null,
            subscription: response.subscription || null,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch {
          get().logout()
        }
      },

      // Set loading state
      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },

      // Update user partially
      updateUser: (userData: Partial<User>) => {
        const { user } = get()
        if (user) {
          set({ user: { ...user, ...userData } })
        }
      },

      // Update organization partially
      updateOrganization: (orgData: Partial<Organization>) => {
        const { organization } = get()
        if (organization) {
          set({ organization: { ...organization, ...orgData } })
        }
      },
    }),
    {
      name: 'aiosol-auth',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
)

// Initialize auth on app load
export const initializeAuth = async () => {
  const { accessToken, fetchMe, setLoading } = useAuthStore.getState()

  if (accessToken) {
    await fetchMe()
  } else {
    setLoading(false)
  }
}
