/**
 * Authentication Types
 * Created by: Karim (Frontend Lead)
 */

export interface User {
  id: string
  email: string
  first_name: string
  last_name?: string
  phone?: string
  avatar_url?: string
  role: UserRole
  is_active: boolean
  is_verified: boolean
  organization_id?: string
  created_at: string
}

export type UserRole =
  | 'super_admin'
  | 'org_owner'
  | 'org_admin'
  | 'org_member'
  | 'org_viewer'

export interface Organization {
  id: string
  name: string
  slug: string
  logo_url?: string
  settings: OrganizationSettings
}

export interface OrganizationSettings {
  timezone: string
  language: string
  currency: string
  reply_delay_min: number
  reply_delay_max: number
  auto_reply_enabled: boolean
  ai_provider: string
  default_tone: string
}

export interface Subscription {
  id: string
  status: SubscriptionStatus
  plan_name: string
  replies_used: number
  replies_limit: number
  pages_used: number
  pages_limit: number
}

export type SubscriptionStatus =
  | 'active'
  | 'trialing'
  | 'cancelled'
  | 'past_due'
  | 'expired'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  first_name: string
  last_name?: string
  organization_name: string
  phone?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface MeResponse {
  user: User
  organization?: Organization
  subscription?: Subscription
}

export interface AuthState {
  user: User | null
  organization: Organization | null
  subscription: Subscription | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
}
