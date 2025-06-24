export interface Role {
  id: number
  name: string
  description?: string
  permissions?: string[]
}

export interface User {
  id: number
  uuid: string
  email: string
  firstName: string
  lastName: string
  first_name?: string  // Backend compatibility
  last_name?: string   // Backend compatibility
  fullName: string
  avatarUrl?: string
  phone?: string
  jobTitle?: string
  department?: string
  bio?: string
  isActive: boolean
  isVerified: boolean
  twoFactorEnabled: boolean
  lastLoginAt?: string
  preferences: UserPreferences
  notificationSettings: NotificationSettings
  tenantId: number
  tenant_id?: number   // Backend compatibility
  primaryRole: string
  role?: string        // Backend compatibility
  roles: Role[]
  createdAt: string
  updatedAt: string
}

export interface UserPreferences {
  language: string
  theme: 'light' | 'dark' | 'system'
  emailFrequency: 'daily' | 'weekly' | 'monthly' | 'never'
  timezone: string
}

export interface NotificationSettings {
  email: boolean
  inApp: boolean
  sms: boolean
  evaluationReminders: boolean
  appointmentReminders: boolean
  newContent: boolean
}

export interface LoginCredentials {
  email: string
  password: string
  tenantId: number
}

export interface RegisterData {
  email: string
  password: string
  firstName: string
  lastName: string
  tenantId: number
  phone?: string
}

export interface UpdateProfileData {
  firstName?: string
  lastName?: string
  phone?: string
  jobTitle?: string
  department?: string
  bio?: string
  preferences?: Partial<UserPreferences>
  notificationSettings?: Partial<NotificationSettings>
}