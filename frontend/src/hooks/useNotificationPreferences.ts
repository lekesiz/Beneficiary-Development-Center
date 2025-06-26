import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { usersApi, NotificationPreferences } from '@/api/users';

export const useNotificationPreferences = () => {
  const queryClient = useQueryClient();

  // Fetch preferences
  const {
    data: preferences,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['user', 'preferences'],
    queryFn: async () => {
      const response = await usersApi.getPreferences();
      return response.data.preferences;
    },
  });

  // Update preferences
  const updatePreferencesMutation = useMutation({
    mutationFn: (newPreferences: NotificationPreferences) => {
      return usersApi.updatePreferences(newPreferences);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['user', 'preferences'], data.data.preferences);
      toast.success('Notification preferences updated successfully');
    },
    onError: (error: any) => {
      toast.error(
        error.response?.data?.message || 'Failed to update notification preferences'
      );
    },
  });

  return {
    preferences,
    isLoading,
    error,
    updatePreferences: updatePreferencesMutation.mutate,
    isUpdating: updatePreferencesMutation.isPending,
    refetch,
  };
};