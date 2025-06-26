import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import apiClient from '@/api/client';

export interface SuggestedMilestone {
  title: string;
  description?: string;
  objective?: string;
  week_number: number;
  estimated_hours: number;
  skill_focus?: string;
  activities: Array<{
    title: string;
    duration: string;
  }>;
  resources: Array<{
    type: string;
    title: string;
    url: string;
  }>;
  assessment_criteria?: string[];
}

export interface LearningPathUpdate {
  id: number;
  learning_path_id: number;
  update_type:
    | 'add_milestone'
    | 'reorder'
    | 'obsolete_milestone'
    | 'modify_milestone';
  source: 'ai' | 'system' | 'manual';
  suggested_milestones: SuggestedMilestone[];
  milestone_updates: Record<string, any>;
  obsolete_milestone_ids: number[];
  reorder_map: Record<string, number>;
  reason: string;
  expected_impact: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'pending' | 'approved' | 'rejected' | 'applied';
  approved_at?: string;
  applied_at?: string;
  rejection_reason?: string;
  created_at: string;
}

// Generate learning path update suggestions
export function useSuggestLearningPathUpdates() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (studentId: number) => {
      const response = await apiClient.post(
        `/api/learning-paths/students/${studentId}/suggest-updates`
      );
      return response.data;
    },
    onSuccess: (data, studentId) => {
      // Invalidate student's learning paths
      queryClient.invalidateQueries({
        queryKey: ['studentLearningPaths', studentId],
      });
    },
  });
}

// Get pending updates for a learning path
export function usePendingLearningPathUpdates(learningPathId: number | null) {
  return useQuery({
    queryKey: ['learningPathUpdates', 'pending', learningPathId],
    queryFn: async () => {
      if (!learningPathId) return null;
      const response = await apiClient.get(
        `/api/learning-paths/${learningPathId}/pending-updates`
      );
      return response.data;
    },
    enabled: !!learningPathId,
  });
}

// Approve a learning path update
export function useApproveLearningPathUpdate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (updateId: number) => {
      const response = await apiClient.post(
        `/api/learning-paths/updates/${updateId}/approve`
      );
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['learningPathUpdates'] });
      queryClient.invalidateQueries({
        queryKey: ['learningPath', data.update.learning_path_id],
      });
    },
  });
}

// Reject a learning path update
export function useRejectLearningPathUpdate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      updateId,
      reason,
    }: {
      updateId: number;
      reason: string;
    }) => {
      const response = await apiClient.post(
        `/api/learning-paths/updates/${updateId}/reject`,
        {
          reason,
        }
      );
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['learningPathUpdates'] });
    },
  });
}

// Apply an approved learning path update
export function useApplyLearningPathUpdate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (updateId: number) => {
      const response = await apiClient.post(
        `/api/learning-paths/updates/${updateId}/apply`
      );
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['learningPathUpdates'] });
      queryClient.invalidateQueries({
        queryKey: ['learningPath', data.learning_path.id],
      });
    },
  });
}

// Get student's active learning paths
export function useStudentLearningPaths(studentId: number | null) {
  return useQuery({
    queryKey: ['studentLearningPaths', studentId],
    queryFn: async () => {
      if (!studentId) return null;
      const response = await apiClient.get('/api/learning-paths/my-paths', {
        params: { user_id: studentId, status: 'accepted,in_progress' },
      });
      return response.data;
    },
    enabled: !!studentId,
  });
}
