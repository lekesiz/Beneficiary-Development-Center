/**
 * React Query hooks for Evaluations
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

import { evaluationsApi } from '../api/evaluations';
import type {
  Evaluation,
  CreateEvaluationRequest,
  UpdateEvaluationRequest,
  EvaluationFilters,
  CreateQuestionRequest,
  UpdateQuestionRequest,
  SaveResponseRequest,
} from '../types/evaluation';

// Query Keys
export const evaluationQueryKeys = {
  all: ['evaluations'] as const,
  lists: () => [...evaluationQueryKeys.all, 'list'] as const,
  list: (filters?: EvaluationFilters) =>
    [...evaluationQueryKeys.lists(), filters] as const,
  details: () => [...evaluationQueryKeys.all, 'detail'] as const,
  detail: (id: number, includeQuestions?: boolean) =>
    [...evaluationQueryKeys.details(), id, includeQuestions] as const,
  questions: (evaluationId: number) =>
    [...evaluationQueryKeys.all, 'questions', evaluationId] as const,
  attempts: (evaluationId: number) =>
    [...evaluationQueryKeys.all, 'attempts', evaluationId] as const,
  attempt: (evaluationId: number, attemptId: number) =>
    [...evaluationQueryKeys.attempts(evaluationId), attemptId] as const,
  myAttempts: (evaluationId: number) =>
    [...evaluationQueryKeys.all, 'my-attempts', evaluationId] as const,
  statistics: () => [...evaluationQueryKeys.all, 'statistics'] as const,
};

/**
 * Hook to get all evaluations with filters
 */
export const useEvaluations = (filters?: EvaluationFilters) => {
  return useQuery({
    queryKey: evaluationQueryKeys.list(filters),
    queryFn: () => evaluationsApi.getAll(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get evaluation by ID
 */
export const useEvaluation = (id: number, includeQuestions = false) => {
  return useQuery({
    queryKey: evaluationQueryKeys.detail(id, includeQuestions),
    queryFn: () => evaluationsApi.getById(id, includeQuestions),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get evaluation questions
 */
export const useEvaluationQuestions = (evaluationId: number) => {
  return useQuery({
    queryKey: evaluationQueryKeys.questions(evaluationId),
    queryFn: () => evaluationsApi.questions.getAll(evaluationId),
    enabled: !!evaluationId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get evaluation statistics
 */
export const useEvaluationStatistics = () => {
  return useQuery({
    queryKey: evaluationQueryKeys.statistics(),
    queryFn: () => evaluationsApi.getStatistics(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Hook to get user's attempts for an evaluation
 */
export const useMyEvaluationAttempts = (evaluationId: number) => {
  return useQuery({
    queryKey: evaluationQueryKeys.myAttempts(evaluationId),
    queryFn: () => evaluationsApi.attempts.getMy(evaluationId),
    enabled: !!evaluationId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Hook to get evaluation attempt details
 */
export const useEvaluationAttempt = (
  evaluationId: number,
  attemptId: number
) => {
  return useQuery({
    queryKey: evaluationQueryKeys.attempt(evaluationId, attemptId),
    queryFn: () => evaluationsApi.attempts.getById(evaluationId, attemptId),
    enabled: !!evaluationId && !!attemptId,
    staleTime: 30 * 1000, // 30 seconds (more frequent updates during active attempts)
  });
};

/**
 * Hook to create evaluation
 */
export const useCreateEvaluation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateEvaluationRequest) => evaluationsApi.create(data),
    onSuccess: (newEvaluation) => {
      // Invalidate and refetch evaluations list
      queryClient.invalidateQueries({ queryKey: evaluationQueryKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.statistics(),
      });

      // Invalidate related course/program details
      if (newEvaluation.course_id) {
        queryClient.invalidateQueries({
          queryKey: ['courses', 'detail', newEvaluation.course_id],
        });
      }
      if (newEvaluation.program_id) {
        queryClient.invalidateQueries({
          queryKey: ['programs', 'detail', newEvaluation.program_id],
        });
      }

      // Add to cache
      queryClient.setQueryData(
        evaluationQueryKeys.detail(newEvaluation.id),
        newEvaluation
      );

      toast.success('Değerlendirme başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message ||
        'Değerlendirme oluşturulurken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to update evaluation
 */
export const useUpdateEvaluation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateEvaluationRequest }) =>
      evaluationsApi.update(id, data),
    onSuccess: (updatedEvaluation) => {
      // Update cached data
      queryClient.setQueryData(
        evaluationQueryKeys.detail(updatedEvaluation.id),
        updatedEvaluation
      );

      // Invalidate lists to refresh
      queryClient.invalidateQueries({ queryKey: evaluationQueryKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.statistics(),
      });

      // Invalidate related course/program details
      if (updatedEvaluation.course_id) {
        queryClient.invalidateQueries({
          queryKey: ['courses', 'detail', updatedEvaluation.course_id],
        });
      }
      if (updatedEvaluation.program_id) {
        queryClient.invalidateQueries({
          queryKey: ['programs', 'detail', updatedEvaluation.program_id],
        });
      }

      toast.success('Değerlendirme başarıyla güncellendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message ||
        'Değerlendirme güncellenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to delete evaluation
 */
export const useDeleteEvaluation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => evaluationsApi.delete(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({
        queryKey: evaluationQueryKeys.detail(deletedId),
      });
      queryClient.removeQueries({
        queryKey: evaluationQueryKeys.questions(deletedId),
      });

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: evaluationQueryKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.statistics(),
      });

      // Invalidate courses and programs to refresh evaluation counts
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      queryClient.invalidateQueries({ queryKey: ['programs'] });

      toast.success('Değerlendirme başarıyla silindi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Değerlendirme silinirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to activate evaluation
 */
export const useActivateEvaluation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => evaluationsApi.activate(id),
    onSuccess: (updatedEvaluation) => {
      // Update cached data
      queryClient.setQueryData(
        evaluationQueryKeys.detail(updatedEvaluation.id),
        updatedEvaluation
      );

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: evaluationQueryKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.statistics(),
      });

      toast.success('Değerlendirme aktifleştirildi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message ||
        'Değerlendirme aktifleştirilirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to archive evaluation
 */
export const useArchiveEvaluation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => evaluationsApi.archive(id),
    onSuccess: (updatedEvaluation) => {
      // Update cached data
      queryClient.setQueryData(
        evaluationQueryKeys.detail(updatedEvaluation.id),
        updatedEvaluation
      );

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: evaluationQueryKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.statistics(),
      });

      toast.success('Değerlendirme arşivlendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message ||
        'Değerlendirme arşivlenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to create question
 */
export const useCreateQuestion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      evaluationId,
      data,
    }: {
      evaluationId: number;
      data: CreateQuestionRequest;
    }) => evaluationsApi.questions.create(evaluationId, data),
    onSuccess: (newQuestion, { evaluationId }) => {
      // Invalidate questions list
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.questions(evaluationId),
      });

      // Invalidate evaluation details to refresh totals
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.detail(evaluationId),
      });

      toast.success('Soru başarıyla eklendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Soru eklenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to update question
 */
export const useUpdateQuestion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      evaluationId,
      questionId,
      data,
    }: {
      evaluationId: number;
      questionId: number;
      data: UpdateQuestionRequest;
    }) => evaluationsApi.questions.update(evaluationId, questionId, data),
    onSuccess: (updatedQuestion, { evaluationId }) => {
      // Invalidate questions list
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.questions(evaluationId),
      });

      // Invalidate evaluation details to refresh totals
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.detail(evaluationId),
      });

      toast.success('Soru başarıyla güncellendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Soru güncellenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to delete question
 */
export const useDeleteQuestion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      evaluationId,
      questionId,
    }: {
      evaluationId: number;
      questionId: number;
    }) => evaluationsApi.questions.delete(evaluationId, questionId),
    onSuccess: (_, { evaluationId }) => {
      // Invalidate questions list
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.questions(evaluationId),
      });

      // Invalidate evaluation details to refresh totals
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.detail(evaluationId),
      });

      toast.success('Soru başarıyla silindi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Soru silinirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to reorder question
 */
export const useReorderQuestion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      evaluationId,
      questionId,
      orderIndex,
    }: {
      evaluationId: number;
      questionId: number;
      orderIndex: number;
    }) =>
      evaluationsApi.questions.reorder(evaluationId, questionId, orderIndex),
    onSuccess: (_, { evaluationId }) => {
      // Invalidate questions list
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.questions(evaluationId),
      });

      toast.success('Soru sırası güncellendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message ||
        'Soru sırası güncellenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to start evaluation attempt
 */
export const useStartEvaluationAttempt = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (evaluationId: number) =>
      evaluationsApi.attempts.start(evaluationId),
    onSuccess: (newAttempt, evaluationId) => {
      // Add to cache
      queryClient.setQueryData(
        evaluationQueryKeys.attempt(evaluationId, newAttempt.id),
        newAttempt
      );

      // Invalidate my attempts list
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.myAttempts(evaluationId),
      });

      toast.success('Değerlendirme başlatıldı');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message ||
        'Değerlendirme başlatılırken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to submit evaluation attempt
 */
export const useSubmitEvaluationAttempt = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      evaluationId,
      attemptId,
    }: {
      evaluationId: number;
      attemptId: number;
    }) => evaluationsApi.attempts.submit(evaluationId, attemptId),
    onSuccess: (submittedAttempt, { evaluationId, attemptId }) => {
      // Update cached attempt
      queryClient.setQueryData(
        evaluationQueryKeys.attempt(evaluationId, attemptId),
        submittedAttempt
      );

      // Invalidate my attempts list
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.myAttempts(evaluationId),
      });

      toast.success('Değerlendirme tamamlandı');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message ||
        'Değerlendirme tamamlanırken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to save question response
 */
export const useSaveQuestionResponse = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      evaluationId,
      attemptId,
      data,
    }: {
      evaluationId: number;
      attemptId: number;
      data: SaveResponseRequest;
    }) => evaluationsApi.attempts.saveResponse(evaluationId, attemptId, data),
    onSuccess: (_, { evaluationId, attemptId }) => {
      // Invalidate attempt details to refresh responses
      queryClient.invalidateQueries({
        queryKey: evaluationQueryKeys.attempt(evaluationId, attemptId),
      });
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Cevap kaydedilirken hata oluştu';
      toast.error(message);
    },
  });
};
