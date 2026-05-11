/**
 * Authentication Service
 * Created by: Karim (Frontend Lead)
 */

import api from './api'
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  MeResponse,
} from '@/types/auth.types'

export const authService = {
  /**
   * Login with email and password
   */
  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/login', data)
    return response.data
  },

  /**
   * Register new user and organization
   */
  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/register', data)
    return response.data
  },

  /**
   * Refresh access token
   */
  async refresh(refreshToken: string): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  /**
   * Get current user profile
   */
  async me(): Promise<MeResponse> {
    const response = await api.get<MeResponse>('/auth/me')
    return response.data
  },

  /**
   * Logout
   */
  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },

  /**
   * Request password reset
   */
  async forgotPassword(email: string): Promise<void> {
    await api.post('/auth/forgot-password', { email })
  },

  /**
   * Reset password with token
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await api.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    })
  },

  /**
   * Change password
   */
  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<void> {
    await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },
}
