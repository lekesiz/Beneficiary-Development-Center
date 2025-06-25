/**
 * React Query hooks for Courses
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

import { coursesApi } from '../api/courses';
import type {
  Course,
  CreateCourseRequest,
  UpdateCourseRequest,
  CourseFilters,
  CreateSessionRequest,
  DuplicateCourseRequest,
  ReorderCourseRequest,
} from '../types/course';

// Query Keys
export const courseQueryKeys = {
  all: ['courses'] as const,
  lists: () => [...courseQueryKeys.all, 'list'] as const,
  list: (filters?: CourseFilters) =>
    [...courseQueryKeys.lists(), filters] as const,
  details: () => [...courseQueryKeys.all, 'detail'] as const,
  detail: (id: number, includeSessions?: boolean) =>
    [...courseQueryKeys.details(), id, includeSessions] as const,
  statistics: (programId?: number) =>
    [...courseQueryKeys.all, 'statistics', programId] as const,
};

/**
 * Hook to get all courses with filters
 */
export const useCourses = (filters?: CourseFilters) => {
  return useQuery({
    queryKey: courseQueryKeys.list(filters),
    queryFn: () => coursesApi.getAll(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get course by ID
 */
export const useCourse = (id: number, includeSessions = false) => {
  return useQuery({
    queryKey: courseQueryKeys.detail(id, includeSessions),
    queryFn: () => coursesApi.getById(id, includeSessions),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get course statistics
 */
export const useCourseStatistics = (programId?: number) => {
  return useQuery({
    queryKey: courseQueryKeys.statistics(programId),
    queryFn: () => coursesApi.getStatistics(programId),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Hook to create course
 */
export const useCreateCourse = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateCourseRequest) => coursesApi.create(data),
    onSuccess: (newCourse) => {
      // Invalidate and refetch courses list
      queryClient.invalidateQueries({ queryKey: courseQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: courseQueryKeys.statistics() });

      // Invalidate related program details
      queryClient.invalidateQueries({
        queryKey: ['programs', 'detail', newCourse.program_id],
      });

      // Add to cache
      queryClient.setQueryData(courseQueryKeys.detail(newCourse.id), newCourse);

      toast.success('Kurs başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.error || 'Kurs oluşturulurken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to update course
 */
export const useUpdateCourse = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateCourseRequest }) =>
      coursesApi.update(id, data),
    onSuccess: (updatedCourse) => {
      // Update cached data
      queryClient.setQueryData(
        courseQueryKeys.detail(updatedCourse.id),
        updatedCourse
      );

      // Invalidate lists to refresh
      queryClient.invalidateQueries({ queryKey: courseQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: courseQueryKeys.statistics() });

      // Invalidate related program details
      queryClient.invalidateQueries({
        queryKey: ['programs', 'detail', updatedCourse.program_id],
      });

      toast.success('Kurs başarıyla güncellendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.error || 'Kurs güncellenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to delete course
 */
export const useDeleteCourse = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => coursesApi.delete(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({
        queryKey: courseQueryKeys.detail(deletedId),
      });

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: courseQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: courseQueryKeys.statistics() });

      // Invalidate programs to refresh course counts
      queryClient.invalidateQueries({ queryKey: ['programs'] });

      toast.success('Kurs başarıyla silindi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.error || 'Kurs silinirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to update course status
 */
export const useUpdateCourseStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      coursesApi.updateStatus(id, status),
    onSuccess: (updatedCourse) => {
      // Update cached data
      queryClient.setQueryData(
        courseQueryKeys.detail(updatedCourse.id),
        updatedCourse
      );

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: courseQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: courseQueryKeys.statistics() });

      toast.success('Kurs durumu güncellendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.error || 'Kurs durumu güncellenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to add session to course
 */
export const useAddSession = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      courseId,
      sessionData,
    }: {
      courseId: number;
      sessionData: CreateSessionRequest;
    }) => coursesApi.addSession(courseId, sessionData),
    onSuccess: (newSession, { courseId }) => {
      // Invalidate course details to refresh sessions
      queryClient.invalidateQueries({
        queryKey: courseQueryKeys.detail(courseId, true),
      });

      toast.success('Oturum başarıyla eklendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.error || 'Oturum eklenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to duplicate course
 */
export const useDuplicateCourse = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      courseId,
      data,
    }: {
      courseId: number;
      data?: DuplicateCourseRequest;
    }) => coursesApi.duplicate(courseId, data),
    onSuccess: (newCourse) => {
      // Invalidate lists to show new course
      queryClient.invalidateQueries({ queryKey: courseQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: courseQueryKeys.statistics() });

      // Invalidate program details if moved to different program
      queryClient.invalidateQueries({ queryKey: ['programs'] });

      // Add to cache
      queryClient.setQueryData(courseQueryKeys.detail(newCourse.id), newCourse);

      toast.success('Kurs başarıyla kopyalandı');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.error || 'Kurs kopyalanırken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to reorder course
 */
export const useReorderCourse = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      courseId,
      data,
    }: {
      courseId: number;
      data: ReorderCourseRequest;
    }) => coursesApi.reorder(courseId, data),
    onSuccess: (updatedCourse) => {
      // Update cached data
      queryClient.setQueryData(
        courseQueryKeys.detail(updatedCourse.id),
        updatedCourse
      );

      // Invalidate lists to refresh order
      queryClient.invalidateQueries({
        queryKey: courseQueryKeys.list({
          program_id: updatedCourse.program_id,
        }),
      });

      // Invalidate program details
      queryClient.invalidateQueries({
        queryKey: ['programs', 'detail', updatedCourse.program_id],
      });

      toast.success('Kurs sırası güncellendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.error || 'Kurs sırası güncellenirken hata oluştu';
      toast.error(message);
    },
  });
};
