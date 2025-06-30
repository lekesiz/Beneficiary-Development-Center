import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import apiClient from '@/api/client';
import type {
  LearningPath,
  LearningMilestone,
  LearningPathStatus,
  LearningPathCreateParams,
  LearningPathUpdateParams,
  MilestoneProgressParams,
} from '@/types/learning-path';

// API client functions
const learningPathApi = {
  // Create a new learning path from evaluation results
  createLearningPath: async (evaluationId: number, attemptId: number): Promise<LearningPath> => {
    const response = await apiClient.post(
      `/api/evaluations/${evaluationId}/attempts/${attemptId}/learning-path`
    );
    return response.data;
  },

  // Get a specific learning path
  getLearningPath: async (pathId: number): Promise<LearningPath> => {
    const response = await apiClient.get(`/api/learning-paths/${pathId}`);
    return response.data;
  },

  // Get user's learning paths
  getMyLearningPaths: async (filters?: {
    status?: string;
    evaluation_id?: number;
  }): Promise<LearningPath[]> => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.evaluation_id) params.append('evaluation_id', filters.evaluation_id.toString());

    const response = await apiClient.get(`/api/learning-paths/my-paths?${params}`);
    return response.data;
  },

  // Accept a learning path
  acceptLearningPath: async (
    pathId: number,
    customizationNotes?: string
  ): Promise<LearningPath> => {
    const response = await apiClient.post(`/api/learning-paths/${pathId}/accept`, {
      customization_notes: customizationNotes,
    });
    return response.data;
  },

  // Update learning path details
  updateLearningPath: async (
    pathId: number,
    updates: LearningPathUpdateParams
  ): Promise<LearningPath> => {
    const response = await apiClient.put(`/api/learning-paths/${pathId}`, updates);
    return response.data;
  },

  // Update milestone progress
  updateMilestoneProgress: async (
    pathId: number,
    milestoneId: number,
    params: MilestoneProgressParams
  ): Promise<LearningMilestone> => {
    const response = await apiClient.put(
      `/api/learning-paths/${pathId}/milestones/${milestoneId}/progress`,
      params
    );
    return response.data;
  },

  // Provide feedback
  provideFeedback: async (
    pathId: number,
    feedback: string,
    rating?: number
  ): Promise<LearningPath> => {
    const response = await apiClient.post(`/api/learning-paths/${pathId}/feedback`, {
      feedback,
      rating,
    });
    return response.data;
  },

  // Get learning path statistics
  getStatistics: async () => {
    const response = await apiClient.get(`/api/learning-paths/statistics`);
    return response.data;
  },
};

// Query key factory
export const learningPathKeys = {
  all: ['learning-paths'] as const,
  lists: () => [...learningPathKeys.all, 'list'] as const,
  list: (filters?: { status?: string; evaluation_id?: number }) =>
    [...learningPathKeys.lists(), filters] as const,
  details: () => [...learningPathKeys.all, 'detail'] as const,
  detail: (id: number) => [...learningPathKeys.details(), id] as const,
  my: (filters?: { status?: string; evaluation_id?: number }) =>
    [...learningPathKeys.all, 'my', filters] as const,
  stats: () => [...learningPathKeys.all, 'stats'] as const,
  milestones: (pathId: number) => [...learningPathKeys.detail(pathId), 'milestones'] as const,
  progress: (pathId: number) => [...learningPathKeys.detail(pathId), 'progress'] as const,
};

// React Query hooks

// Create learning path from evaluation
export const useCreateLearningPath = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ evaluationId, attemptId }: { evaluationId: number; attemptId: number }) =>
      learningPathApi.createLearningPath(evaluationId, attemptId),
    onSuccess: (data) => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: learningPathKeys.all });
      queryClient.invalidateQueries({ queryKey: ['learning-path-stats'] });
      // Set the new learning path in cache
      queryClient.setQueryData(learningPathKeys.detail(data.id), data);
    },
  });
};

// Get a specific learning path
export const useLearningPath = (pathId: number) => {
  return useQuery({
    queryKey: learningPathKeys.detail(pathId),
    queryFn: () => learningPathApi.getLearningPath(pathId),
    enabled: !!pathId,
  });
};

// Get user's learning paths
export const useMyLearningPaths = (filters?: { status?: string; evaluation_id?: number }) => {
  return useQuery({
    queryKey: learningPathKeys.my(filters),
    queryFn: () => learningPathApi.getMyLearningPaths(filters),
  });
};

// Accept learning path
export const useAcceptLearningPath = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ pathId, customizationNotes }: { pathId: number; customizationNotes?: string }) =>
      learningPathApi.acceptLearningPath(pathId, customizationNotes),
    onSuccess: (data) => {
      // Update the learning path in cache
      queryClient.setQueryData(learningPathKeys.detail(data.id), data);
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: learningPathKeys.all });
    },
  });
};

// Update learning path
export const useUpdateLearningPath = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ pathId, updates }: { pathId: number; updates: LearningPathUpdateParams }) =>
      learningPathApi.updateLearningPath(pathId, updates),
    onSuccess: (data) => {
      // Update the learning path in cache
      queryClient.setQueryData(learningPathKeys.detail(data.id), data);
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: learningPathKeys.all });
    },
  });
};

// Update milestone progress
export const useUpdateMilestoneProgress = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      pathId,
      milestoneId,
      progress,
      notes,
    }: {
      pathId: number;
      milestoneId: number;
      progress: number;
      notes?: string;
    }) =>
      learningPathApi.updateMilestoneProgress(pathId, milestoneId, {
        progress,
        notes,
      }),
    onSuccess: (data, variables) => {
      // Invalidate the learning path to refresh milestone data
      queryClient.invalidateQueries({
        queryKey: ['learning-path', variables.pathId],
      });
    },
  });
};

// Provide feedback
export const useProvideFeedback = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      pathId,
      feedback,
      rating,
    }: {
      pathId: number;
      feedback: string;
      rating?: number;
    }) => learningPathApi.provideFeedback(pathId, feedback, rating),
    onSuccess: (data) => {
      // Update the learning path in cache
      queryClient.setQueryData(learningPathKeys.detail(data.id), data);
    },
  });
};

// Get learning path statistics
export const useLearningPathStatistics = () => {
  return useQuery({
    queryKey: ['learning-path-stats'],
    queryFn: learningPathApi.getStatistics,
  });
};
