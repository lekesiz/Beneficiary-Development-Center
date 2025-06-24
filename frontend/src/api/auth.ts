import apiClient from './client'
import { LoginCredentials, RegisterData, User } from '@/types/user'

export const authApi = {
  login: (credentials: LoginCredentials) => {
    return apiClient.post('/auth/login', credentials)
  },

  register: (data: RegisterData) => {
    return apiClient.post('/auth/register', data)
  },

  logout: () => {
    return apiClient.post('/auth/logout')
  },

  refreshToken: () => {
    return apiClient.post('/auth/refresh')
  },

  getCurrentUser: () => {
    return apiClient.get<{ user: User }>('/auth/me')
  },

  forgotPassword: (email: string, tenantId: number) => {
    return apiClient.post('/auth/forgot-password', { email, tenantId })
  },

  resetPassword: (token: string, password: string) => {
    return apiClient.post('/auth/reset-password', { token, password })
  },

  changePassword: (oldPassword: string, newPassword: string) => {
    return apiClient.post('/auth/change-password', { oldPassword, newPassword })
  },

  verifyEmail: (token: string) => {
    return apiClient.get(`/auth/verify-email/${token}`)
  },
}