import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '@/api/auth'
import { User } from '@/types/user'
import toast from 'react-hot-toast'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string, tenantId: number) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  updateUser: (user: User) => void
}

interface RegisterData {
  email: string
  password: string
  firstName: string
  lastName: string
  tenantId: number
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  const isAuthenticated = !!user

  useEffect(() => {
    // Check if user is logged in on mount
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      const response = await authApi.getCurrentUser()
      setUser(response.data.user)
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string, tenantId: number) => {
    try {
      const response = await authApi.login({ email, password, tenantId })
      const { user, access_token, refresh_token } = response.data

      // Store tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('tenant_id', tenantId.toString())

      // Set user
      setUser(user)

      // Show success message
      toast.success(`Welcome back, ${user.firstName}!`)

      // Navigate to dashboard
      navigate('/dashboard')
    } catch (error: any) {
      const message = error.response?.data?.message || 'Login failed'
      toast.error(message)
      throw error
    }
  }

  const register = async (data: RegisterData) => {
    try {
      const response = await authApi.register(data)
      const { user, access_token, refresh_token } = response.data

      // Store tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('tenant_id', data.tenantId.toString())

      // Set user
      setUser(user)

      // Show success message
      toast.success('Registration successful!')

      // Navigate to dashboard
      navigate('/dashboard')
    } catch (error: any) {
      const message = error.response?.data?.message || 'Registration failed'
      toast.error(message)
      throw error
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear tokens and user data
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('tenant_id')
      setUser(null)

      // Navigate to login
      navigate('/login')
      toast.success('Logged out successfully')
    }
  }

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        throw new Error('No refresh token')
      }

      const response = await authApi.refreshToken()
      const { access_token } = response.data

      // Update access token
      localStorage.setItem('access_token', access_token)
    } catch (error) {
      // If refresh fails, logout
      await logout()
      throw error
    }
  }

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser)
  }

  const value = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken,
    updateUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}