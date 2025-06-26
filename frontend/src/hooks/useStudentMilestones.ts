import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import apiClient from '@/api/client';

export interface MilestoneActivity {
  title: string;
  duration: string;
}

export interface MilestoneResource {
  type: string;
  title: string;
  url: string;
}

export interface StudentMilestone {
  id: number;
  title: string;
  description: string;
  objective: string;
  week_number: number;
  estimated_hours: number;
  skill_focus: string;
  status: 'pending' | 'in_progress' | 'completed';
  progress: number;
  activities: MilestoneActivity[];
  resources: MilestoneResource[];
  completed_activities?: number[];
  started_at?: string;
  completed_at?: string;
  help_requested?: boolean;
  learning_path_id: number;
  learning_path_title: string;
}

// Get student's milestones
export function useStudentMilestones() {
  return useQuery({
    queryKey: ['studentMilestones'],
    queryFn: async () => {
      const response = await apiClient.get('/api/learning-paths/student/milestones');
      return response.data.milestones as StudentMilestone[];
    },
  });
}

// Start a milestone
export function useStartMilestone() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (milestoneId: number) => {
      const response = await apiClient.post(
        `/api/learning-paths/milestones/${milestoneId}/start`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studentMilestones'] });
    },
  });
}

// Complete a milestone
export function useCompleteMilestone() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (milestoneId: number) => {
      const response = await apiClient.post(
        `/api/learning-paths/milestones/${milestoneId}/complete`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studentMilestones'] });
    },
  });
}

// Update milestone progress
export function useUpdateMilestoneProgress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      milestoneId,
      progress,
      completedActivities,
    }: {
      milestoneId: number;
      progress: number;
      completedActivities?: number[];
    }) => {
      const response = await apiClient.patch(
        `/api/learning-paths/milestones/${milestoneId}/progress`,
        {
          progress,
          completed_activities: completedActivities,
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studentMilestones'] });
    },
  });
}

// Request help for a milestone
export function useRequestHelp() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      milestoneId,
      message,
    }: {
      milestoneId: number;
      message: string;
    }) => {
      const response = await apiClient.post(
        `/api/learning-paths/milestones/${milestoneId}/help`,
        {
          message,
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studentMilestones'] });
    },
  });
}

// Get milestone details
export function useMilestoneDetails(milestoneId: number | null) {
  return useQuery({
    queryKey: ['milestoneDetails', milestoneId],
    queryFn: async () => {
      if (!milestoneId) return null;
      const response = await apiClient.get(
        `/api/learning-paths/milestones/${milestoneId}`
      );
      return response.data.milestone as StudentMilestone;
    },
    enabled: !!milestoneId,
  });
}

// Mark activity as completed
export function useCompleteActivity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      milestoneId,
      activityIndex,
    }: {
      milestoneId: number;
      activityIndex: number;
    }) => {
      const response = await apiClient.post(
        `/api/learning-paths/milestones/${milestoneId}/activities/${activityIndex}/complete`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studentMilestones'] });
    },
  });
}
