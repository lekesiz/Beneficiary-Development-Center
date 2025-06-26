/**
 * Hook for managing course sessions
 */

import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { CourseSession } from '../types/course';

interface SessionWithCourse extends CourseSession {
  course?: {
    id: number;
    title: string;
    code: string;
    program_id: number;
  };
}

interface UseSessionsParams {
  include_past?: boolean;
  include_cancelled?: boolean;
  instructor_id?: number | null;
  course_id?: number;
  program_id?: number;
}

/**
 * Hook to fetch all sessions for the current user
 * This would need a backend endpoint that returns all sessions across all courses
 */
export const useSessions = (params: UseSessionsParams = {}) => {
  return useQuery<SessionWithCourse[]>({
    queryKey: ['sessions', params],
    queryFn: async () => {
      // This endpoint would need to be created in the backend
      // For now, we'll assume it exists at /api/v1/sessions
      const queryParams = new URLSearchParams();
      
      if (params.include_past !== undefined) {
        queryParams.append('include_past', params.include_past.toString());
      }
      if (params.include_cancelled !== undefined) {
        queryParams.append('include_cancelled', params.include_cancelled.toString());
      }
      if (params.instructor_id) {
        queryParams.append('instructor_id', params.instructor_id.toString());
      }
      if (params.course_id) {
        queryParams.append('course_id', params.course_id.toString());
      }
      if (params.program_id) {
        queryParams.append('program_id', params.program_id.toString());
      }
      
      const response = await api.get(`/sessions?${queryParams.toString()}`);
      return response.data.sessions;
    },
  });
};

/**
 * Hook to fetch sessions for a specific course
 */
export const useCourseSessions = (
  programId: number,
  courseId: number,
  params: Omit<UseSessionsParams, 'course_id' | 'program_id'> = {}
) => {
  return useQuery<CourseSession[]>({
    queryKey: ['course-sessions', programId, courseId, params],
    queryFn: async () => {
      const queryParams = new URLSearchParams();
      
      if (params.include_past !== undefined) {
        queryParams.append('include_past', params.include_past.toString());
      }
      if (params.include_cancelled !== undefined) {
        queryParams.append('include_cancelled', params.include_cancelled.toString());
      }
      
      const response = await api.get(
        `/programs/${programId}/courses/${courseId}/sessions?${queryParams.toString()}`
      );
      return response.data.sessions;
    },
    enabled: !!programId && !!courseId,
  });
};