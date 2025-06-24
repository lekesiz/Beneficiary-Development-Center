/**
 * Custom hook for adaptive evaluation features
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { evaluationsApi, AdaptiveQuestionResponse, LearningInsights } from '@/api/evaluations';
import { useToast } from '@/hooks/useToast';

/**
 * Hook to get next adaptive question
 */
export const useAdaptiveNextQuestion = () => {
  const toast = useToast();

  return useMutation<
    AdaptiveQuestionResponse,
    Error,
    { evaluationId: number; attemptId: number; currentIndex?: number }
  >({
    mutationFn: ({ evaluationId, attemptId, currentIndex }) =>
      evaluationsApi.adaptive.getNextQuestion(evaluationId, attemptId, currentIndex),
    onError: (error) => {
      toast.error('Sonraki soru alınamadı. Lütfen tekrar deneyin.');
      console.error('Error getting next adaptive question:', error);
    }
  });
};

/**
 * Hook to get learning insights for an attempt
 */
export const useLearningInsights = (evaluationId: number, attemptId: number, enabled = true) => {
  return useQuery<LearningInsights, Error>({
    queryKey: ['learningInsights', evaluationId, attemptId],
    queryFn: () => evaluationsApi.adaptive.getLearningInsights(evaluationId, attemptId),
    enabled: enabled && !!evaluationId && !!attemptId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false
  });
};

/**
 * Hook to manage the entire adaptive evaluation flow
 */
export const useAdaptiveEvaluationFlow = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  const getNextQuestion = useAdaptiveNextQuestion();

  const prefetchNextQuestions = async (evaluationId: number, attemptId: number, currentIndex: number) => {
    // Prefetch the next 2 questions for better performance
    for (let i = 1; i <= 2; i++) {
      queryClient.prefetchQuery({
        queryKey: ['adaptiveQuestion', evaluationId, attemptId, currentIndex + i],
        queryFn: () => evaluationsApi.adaptive.getNextQuestion(evaluationId, attemptId, currentIndex + i),
        staleTime: 30 * 1000 // 30 seconds
      });
    }
  };

  const invalidateAdaptiveCache = (evaluationId: number, attemptId: number) => {
    // Invalidate cached adaptive questions when needed
    queryClient.invalidateQueries({
      queryKey: ['adaptiveQuestion', evaluationId, attemptId]
    });
  };

  return {
    getNextQuestion,
    prefetchNextQuestions,
    invalidateAdaptiveCache
  };
};

// Helper function to determine difficulty badge color
export const getDifficultyColor = (difficulty: 'easy' | 'medium' | 'hard'): string => {
  switch (difficulty) {
    case 'easy':
      return 'bg-green-100 text-green-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'hard':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

// Helper function to get difficulty label in Turkish
export const getDifficultyLabel = (difficulty: 'easy' | 'medium' | 'hard'): string => {
  switch (difficulty) {
    case 'easy':
      return 'Kolay';
    case 'medium':
      return 'Orta';
    case 'hard':
      return 'Zor';
    default:
      return difficulty;
  }
};