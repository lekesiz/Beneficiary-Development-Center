import { Bell, Mail, Smartphone } from 'lucide-react';
import React, { useState, useEffect } from 'react';

import { NotificationPreferences } from '@/api/users';
import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { useNotificationPreferences } from '@/hooks/useNotificationPreferences';

interface NotificationCategory {
  key: keyof NotificationPreferences['notifications']['email'];
  label: string;
  description: string;
}

const notificationCategories: NotificationCategory[] = [
  {
    key: 'new_message',
    label: 'New Messages',
    description: 'Receive notifications when you get a new message',
  },
  {
    key: 'appointment_reminder',
    label: 'Appointment Reminders',
    description: 'Get reminded about upcoming appointments',
  },
  {
    key: 'evaluation_completed',
    label: 'Evaluation Completed',
    description: 'Be notified when evaluations are completed',
  },
  {
    key: 'course_enrollment',
    label: 'Course Enrollment',
    description: 'Updates about course enrollments and changes',
  },
  {
    key: 'program_update',
    label: 'Program Updates',
    description: 'Important updates about programs you are involved in',
  },
];

export const NotificationSettings: React.FC = () => {
  const { preferences, isLoading, updatePreferences, isUpdating } = useNotificationPreferences();
  const [localPreferences, setLocalPreferences] = useState<NotificationPreferences | null>(null);

  useEffect(() => {
    if (preferences) {
      setLocalPreferences(preferences);
    }
  }, [preferences]);

  const handleToggle = (
    channel: 'email' | 'in_app',
    category: keyof NotificationPreferences['notifications']['email']
  ) => {
    if (!localPreferences) return;

    const newPreferences = {
      ...localPreferences,
      notifications: {
        ...localPreferences.notifications,
        [channel]: {
          ...localPreferences.notifications[channel],
          [category]: !localPreferences.notifications[channel][category],
        },
      },
    };

    setLocalPreferences(newPreferences);
    updatePreferences(newPreferences);
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!localPreferences) {
    return (
      <Card>
        <div className="p-6 text-center text-gray-500">
          Failed to load notification preferences
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Notification Preferences</h3>
        <p className="mt-1 text-sm text-gray-500">
          Choose how you want to be notified about important updates and activities.
        </p>
      </div>

      <Card>
        <div className="p-6">
          <div className="space-y-6">
            {/* Header */}
            <div className="grid grid-cols-3 gap-4 pb-4 border-b border-gray-200">
              <div className="col-span-1">
                <span className="text-sm font-medium text-gray-700">Notification Type</span>
              </div>
              <div className="col-span-2 grid grid-cols-2 gap-4">
                <div className="flex items-center justify-center space-x-2">
                  <Mail className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-700">Email</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <Bell className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-700">In-App</span>
                </div>
              </div>
            </div>

            {/* Notification Categories */}
            {notificationCategories.map((category) => (
              <div key={category.key} className="grid grid-cols-3 gap-4 items-center">
                <div className="col-span-1">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{category.label}</p>
                    <p className="text-xs text-gray-500">{category.description}</p>
                  </div>
                </div>
                <div className="col-span-2 grid grid-cols-2 gap-4">
                  <div className="flex justify-center">
                    <button
                      type="button"
                      onClick={() => handleToggle('email', category.key)}
                      disabled={isUpdating}
                      className={`
                        relative inline-flex h-6 w-11 items-center rounded-full
                        transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                        ${localPreferences.notifications.email[category.key] 
                          ? 'bg-primary-600' 
                          : 'bg-gray-200'
                        }
                        ${isUpdating ? 'opacity-50 cursor-not-allowed' : ''}
                      `}
                      aria-label={`Toggle email notifications for ${category.label}`}
                    >
                      <span
                        className={`
                          inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                          ${localPreferences.notifications.email[category.key] 
                            ? 'translate-x-6' 
                            : 'translate-x-1'
                          }
                        `}
                      />
                    </button>
                  </div>
                  <div className="flex justify-center">
                    <button
                      type="button"
                      onClick={() => handleToggle('in_app', category.key)}
                      disabled={isUpdating}
                      className={`
                        relative inline-flex h-6 w-11 items-center rounded-full
                        transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                        ${localPreferences.notifications.in_app[category.key] 
                          ? 'bg-primary-600' 
                          : 'bg-gray-200'
                        }
                        ${isUpdating ? 'opacity-50 cursor-not-allowed' : ''}
                      `}
                      aria-label={`Toggle in-app notifications for ${category.label}`}
                    >
                      <span
                        className={`
                          inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                          ${localPreferences.notifications.in_app[category.key] 
                            ? 'translate-x-6' 
                            : 'translate-x-1'
                          }
                        `}
                      />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Smartphone className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">SMS Notifications</h3>
            <div className="mt-2 text-sm text-blue-700">
              SMS notifications are not currently available. We'll notify you when this feature becomes available.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};