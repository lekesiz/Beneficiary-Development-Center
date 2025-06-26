import apiClient from './client';

export interface NotificationPreferences {
  notifications: {
    email: {
      new_message: boolean;
      appointment_reminder: boolean;
      evaluation_completed: boolean;
      course_enrollment: boolean;
      program_update: boolean;
    };
    in_app: {
      new_message: boolean;
      appointment_reminder: boolean;
      evaluation_completed: boolean;
      course_enrollment: boolean;
      program_update: boolean;
    };
  };
}

export const usersApi = {
  // Get current user's notification preferences
  getPreferences: () => {
    return apiClient.get<{ preferences: NotificationPreferences }>('/users/me/preferences');
  },

  // Update current user's notification preferences
  updatePreferences: (preferences: NotificationPreferences) => {
    return apiClient.put<{ 
      message: string; 
      preferences: NotificationPreferences 
    }>('/users/me/preferences', preferences);
  },
};