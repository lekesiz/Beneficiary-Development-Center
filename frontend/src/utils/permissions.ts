import { User } from '@/types/user';

// Standard role definitions that match backend
export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  ADMIN: 'admin', 
  TRAINER: 'trainer',
  STUDENT: 'student'
} as const;

export type Role = typeof ROLES[keyof typeof ROLES];

// Permission groups for easier management
export const PERMISSION_GROUPS = {
  USER_MANAGEMENT: [ROLES.SUPER_ADMIN, ROLES.ADMIN],
  PROGRAM_MANAGEMENT: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.TRAINER],
  BENEFICIARY_MANAGEMENT: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.TRAINER],
  COURSE_CREATION: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.TRAINER],
  EVALUATION_CREATION: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.TRAINER],
  SYSTEM_SETTINGS: [ROLES.SUPER_ADMIN, ROLES.ADMIN],
  VIEW_REPORTS: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.TRAINER],
  VIEW_ALL_DATA: [ROLES.SUPER_ADMIN, ROLES.ADMIN],
  VIEW_ASSIGNED_DATA: [ROLES.TRAINER, ROLES.STUDENT],
} as const;

/**
 * Check if user has a specific role
 */
export const hasRole = (user: User | null, role: Role): boolean => {
  if (!user) return false;
  
  // Check roles array first (preferred method)
  if (user.roles?.some(r => r.name === role)) return true;
  
  // Fallback to primaryRole
  if (user.primaryRole === role) return true;
  
  // Legacy fallback to role property
  if (user.role === role) return true;
  
  return false;
};

/**
 * Check if user has any of the specified roles
 */
export const hasAnyRole = (user: User | null, roles: Role[]): boolean => {
  if (!user) return false;
  return roles.some(role => hasRole(user, role));
};

/**
 * Check if user has all of the specified roles
 */
export const hasAllRoles = (user: User | null, roles: Role[]): boolean => {
  if (!user) return false;
  return roles.every(role => hasRole(user, role));
};

/**
 * Check if user can manage other users
 */
export const canManageUsers = (user: User | null): boolean => {
  return hasAnyRole(user, PERMISSION_GROUPS.USER_MANAGEMENT);
};

/**
 * Check if user can create/edit programs
 */
export const canManagePrograms = (user: User | null): boolean => {
  return hasAnyRole(user, PERMISSION_GROUPS.PROGRAM_MANAGEMENT);
};

/**
 * Check if user can manage beneficiaries
 */
export const canManageBeneficiaries = (user: User | null): boolean => {
  return hasAnyRole(user, PERMISSION_GROUPS.BENEFICIARY_MANAGEMENT);
};

/**
 * Check if user can create/edit courses
 */
export const canManageCourses = (user: User | null): boolean => {
  return hasAnyRole(user, PERMISSION_GROUPS.COURSE_CREATION);
};

/**
 * Check if user can create/edit evaluations
 */
export const canManageEvaluations = (user: User | null): boolean => {
  return hasAnyRole(user, PERMISSION_GROUPS.EVALUATION_CREATION);
};

/**
 * Check if user can access system settings
 */
export const canAccessSystemSettings = (user: User | null): boolean => {
  return hasAnyRole(user, PERMISSION_GROUPS.SYSTEM_SETTINGS);
};

/**
 * Check if user can view reports
 */
export const canViewReports = (user: User | null): boolean => {
  return hasAnyRole(user, PERMISSION_GROUPS.VIEW_REPORTS);
};

/**
 * Check if user can view all data (admin level)
 */
export const canViewAllData = (user: User | null): boolean => {
  return hasAnyRole(user, PERMISSION_GROUPS.VIEW_ALL_DATA);
};

/**
 * Check if user can only view assigned data
 */
export const canViewAssignedDataOnly = (user: User | null): boolean => {
  return hasAnyRole(user, PERMISSION_GROUPS.VIEW_ASSIGNED_DATA) && !canViewAllData(user);
};

/**
 * Check if user is an admin (admin or super_admin)
 */
export const isAdmin = (user: User | null): boolean => {
  return hasAnyRole(user, [ROLES.SUPER_ADMIN, ROLES.ADMIN]);
};

/**
 * Check if user is a trainer
 */
export const isTrainer = (user: User | null): boolean => {
  return hasRole(user, ROLES.TRAINER);
};

/**
 * Check if user is a student
 */
export const isStudent = (user: User | null): boolean => {
  return hasRole(user, ROLES.STUDENT);
};

/**
 * Check if user is super admin
 */
export const isSuperAdmin = (user: User | null): boolean => {
  return hasRole(user, ROLES.SUPER_ADMIN);
};

/**
 * Get user's highest role priority for display purposes
 */
export const getHighestRole = (user: User | null): Role | null => {
  if (!user) return null;
  
  const rolePriority = [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.TRAINER, ROLES.STUDENT];
  
  for (const role of rolePriority) {
    if (hasRole(user, role)) {
      return role;
    }
  }
  
  return ROLES.STUDENT; // Default fallback
};

/**
 * Get user's role display name
 */
export const getRoleDisplayName = (role: Role): string => {
  const displayNames = {
    [ROLES.SUPER_ADMIN]: 'Super Administrator',
    [ROLES.ADMIN]: 'Administrator', 
    [ROLES.TRAINER]: 'Trainer',
    [ROLES.STUDENT]: 'Student'
  };
  
  return displayNames[role] || 'Unknown';
};

/**
 * Check if user can perform a specific action on a resource
 * @param user Current user
 * @param action Action to check (create, read, update, delete)
 * @param resource Resource type (program, beneficiary, course, etc.)
 * @param resourceOwnerId Optional - ID of the resource owner for ownership checks
 */
export const canPerformAction = (
  user: User | null,
  action: 'create' | 'read' | 'update' | 'delete',
  resource: 'program' | 'beneficiary' | 'course' | 'evaluation' | 'user' | 'setting',
  resourceOwnerId?: number
): boolean => {
  if (!user) return false;
  
  // Super admin can do everything
  if (isSuperAdmin(user)) return true;
  
  // Admin can do most things
  if (isAdmin(user)) {
    if (resource === 'user' && action === 'delete') {
      // Only super admin can delete users
      return false;
    }
    return true;
  }
  
  // Trainer permissions
  if (isTrainer(user)) {
    switch (resource) {
      case 'program':
      case 'course':
      case 'evaluation':
        return ['create', 'read', 'update'].includes(action);
      case 'beneficiary':
        return ['read', 'update'].includes(action);
      case 'user':
        // Can only read and update own profile
        return action === 'read' || (action === 'update' && resourceOwnerId === user.id);
      case 'setting':
        return false; // Cannot access system settings
      default:
        return false;
    }
  }
  
  // Student permissions
  if (isStudent(user)) {
    switch (resource) {
      case 'program':
      case 'course':
      case 'evaluation':
        return action === 'read';
      case 'beneficiary':
        // Can only read/update own data
        return ['read', 'update'].includes(action) && resourceOwnerId === user.id;
      case 'user':
        // Can only read and update own profile
        return action === 'read' || (action === 'update' && resourceOwnerId === user.id);
      case 'setting':
        return false;
      default:
        return false;
    }
  }
  
  return false;
};

/**
 * Validation helper to ensure role consistency
 */
export const validateUserRoles = (user: User): { isValid: boolean; issues: string[] } => {
  const issues: string[] = [];
  
  if (!user.roles || user.roles.length === 0) {
    issues.push('User has no roles assigned');
  }
  
  if (user.primaryRole && !hasRole(user, user.primaryRole as Role)) {
    issues.push('Primary role does not match assigned roles');
  }
  
  // Check for invalid role names
  const validRoleNames = Object.values(ROLES);
  const invalidRoles = user.roles?.filter(role => !validRoleNames.includes(role.name as Role)) || [];
  if (invalidRoles.length > 0) {
    issues.push(`Invalid roles found: ${invalidRoles.map(r => r.name).join(', ')}`);
  }
  
  return {
    isValid: issues.length === 0,
    issues
  };
};