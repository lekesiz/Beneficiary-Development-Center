/**
 * React Query hooks for Programs
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

import { programsApi } from '../api/programs';
import type {
  Program,
  CreateProgramRequest,
  UpdateProgramRequest,
  ProgramFilters,
  CreateCourseInProgramRequest,
} from '../types/program';

// Query Keys
export const programQueryKeys = {
  all: ['programs'] as const,
  lists: () => [...programQueryKeys.all, 'list'] as const,
  list: (filters?: ProgramFilters) => [...programQueryKeys.lists(), filters] as const,
  details: () => [...programQueryKeys.all, 'detail'] as const,
  detail: (id: number, includeCourses?: boolean) =>
    [...programQueryKeys.details(), id, includeCourses] as const,
  statistics: () => [...programQueryKeys.all, 'statistics'] as const,
};

/**
 * Hook to get all programs with filters
 */
export const usePrograms = (filters?: ProgramFilters) => {
  return useQuery({
    queryKey: programQueryKeys.list(filters),
    queryFn: () => programsApi.getAll(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get program by ID
 */
export const useProgram = (id: number, includeCourses = false) => {
  return useQuery({
    queryKey: programQueryKeys.detail(id, includeCourses),
    queryFn: () => programsApi.getById(id, includeCourses),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get program statistics
 */
export const useProgramStatistics = () => {
  return useQuery({
    queryKey: programQueryKeys.statistics(),
    queryFn: programsApi.getStatistics,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Hook to create program
 */
export const useCreateProgram = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProgramRequest) => programsApi.create(data),
    onSuccess: (newProgram) => {
      // Invalidate and refetch programs list
      queryClient.invalidateQueries({ queryKey: programQueryKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: programQueryKeys.statistics(),
      });

      // Add to cache
      queryClient.setQueryData(programQueryKeys.detail(newProgram.id), newProgram);

      toast.success('Program başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Program oluşturulurken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to update program
 */
export const useUpdateProgram = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateProgramRequest }) =>
      programsApi.update(id, data),
    onSuccess: (updatedProgram) => {
      // Update cached data
      queryClient.setQueryData(programQueryKeys.detail(updatedProgram.id), updatedProgram);

      // Invalidate lists to refresh
      queryClient.invalidateQueries({ queryKey: programQueryKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: programQueryKeys.statistics(),
      });

      toast.success('Program başarıyla güncellendi');
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Program güncellenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to delete program
 */
export const useDeleteProgram = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => programsApi.delete(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({
        queryKey: programQueryKeys.detail(deletedId),
      });

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: programQueryKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: programQueryKeys.statistics(),
      });

      toast.success('Program başarıyla silindi');
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Program silinirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to update program status
 */
export const useUpdateProgramStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      programsApi.updateStatus(id, status),
    onSuccess: (updatedProgram) => {
      // Update cached data
      queryClient.setQueryData(programQueryKeys.detail(updatedProgram.id), updatedProgram);

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: programQueryKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: programQueryKeys.statistics(),
      });

      toast.success('Program durumu güncellendi');
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Program durumu güncellenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to add course to program
 */
export const useAddCourseToProgram = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      programId,
      courseData,
    }: {
      programId: number;
      courseData: CreateCourseInProgramRequest;
    }) => programsApi.addCourse(programId, courseData),
    onSuccess: (newCourse, { programId }) => {
      // Invalidate program details to refresh courses
      queryClient.invalidateQueries({
        queryKey: programQueryKeys.detail(programId, true),
      });

      // Invalidate courses lists
      queryClient.invalidateQueries({ queryKey: ['courses'] });

      toast.success('Kurs programa başarıyla eklendi');
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Kurs eklenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to get courses for a specific program
 */
export const useProgramCourses = (programId: number) => {
  return useQuery({
    queryKey: ['programs', programId, 'courses'] as const,
    queryFn: async () => {
      const { data } = await programsApi.getById(programId, true);
      return { courses: data.courses || [] };
    },
    enabled: !!programId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
