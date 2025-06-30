import { User } from '@/types/user';

export function transformUserFromBackend(backendUser: any): User {
  return {
    id: backendUser.id,
    uuid: backendUser.uuid,
    email: backendUser.email,
    firstName: backendUser.first_name,
    lastName: backendUser.last_name,
    first_name: backendUser.first_name, // Keep for backward compatibility
    last_name: backendUser.last_name, // Keep for backward compatibility
    fullName: backendUser.full_name || `${backendUser.first_name} ${backendUser.last_name}`,
    avatarUrl: backendUser.avatar_url,
    phone: backendUser.phone,
    jobTitle: backendUser.job_title,
    department: backendUser.department,
    bio: backendUser.bio,
    isActive: backendUser.is_active,
    isVerified: backendUser.is_verified,
    twoFactorEnabled: backendUser.two_factor_enabled || false,
    lastLoginAt: backendUser.last_login_at,
    preferences: backendUser.preferences || {
      language: 'en',
      theme: 'light',
      emailFrequency: 'daily',
      timezone: 'UTC',
    },
    notificationSettings: backendUser.notification_settings || {
      email: true,
      inApp: true,
      sms: false,
      evaluationReminders: true,
      appointmentReminders: true,
      newContent: true,
    },
    tenantId: backendUser.tenant_id,
    tenant_id: backendUser.tenant_id, // Keep for backward compatibility
    primaryRole: backendUser.primary_role || backendUser.role || 'student',
    role: backendUser.role,
    roles: backendUser.roles || [],
    createdAt: backendUser.created_at,
    updatedAt: backendUser.updated_at,
  };
}