/**
 * Courses API client
 */
import type {
  Course,
  CreateCourseRequest,
  UpdateCourseRequest,
  CourseFilters,
  CoursesResponse,
  CourseSession,
  CreateSessionRequest,
  DuplicateCourseRequest,
  ReorderCourseRequest,
  CourseStatistics,
} from '../types/course';

import { apiClient } from './client';

const COURSES_BASE_URL = '/courses';

export const coursesApi = {
  /**
   * Get all courses with optional filters
   */
  getAll: async (filters?: CourseFilters): Promise<CoursesResponse> => {
    const params = new URLSearchParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }

    const response = await apiClient.get<CoursesResponse>(
      `${COURSES_BASE_URL}?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get course by ID
   */
  getById: async (id: number, includeSessions = false): Promise<Course> => {
    const params = includeSessions ? '?include_sessions=true' : '';
    const response = await apiClient.get<Course>(
      `${COURSES_BASE_URL}/${id}${params}`
    );
    return response.data;
  },

  /**
   * Create new course
   */
  create: async (data: CreateCourseRequest): Promise<Course> => {
    const response = await apiClient.post<Course>(COURSES_BASE_URL, data);
    return response.data;
  },

  /**
   * Update course
   */
  update: async (id: number, data: UpdateCourseRequest): Promise<Course> => {
    const response = await apiClient.put<Course>(
      `${COURSES_BASE_URL}/${id}`,
      data
    );
    return response.data;
  },

  /**
   * Delete course
   */
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`${COURSES_BASE_URL}/${id}`);
  },

  /**
   * Add session to course
   */
  addSession: async (
    courseId: number,
    sessionData: CreateSessionRequest
  ): Promise<CourseSession> => {
    const response = await apiClient.post<CourseSession>(
      `${COURSES_BASE_URL}/${courseId}/sessions`,
      sessionData
    );
    return response.data;
  },

  /**
   * Duplicate course
   */
  duplicate: async (
    courseId: number,
    data?: DuplicateCourseRequest
  ): Promise<Course> => {
    const response = await apiClient.post<Course>(
      `${COURSES_BASE_URL}/${courseId}/duplicate`,
      data || {}
    );
    return response.data;
  },

  /**
   * Reorder course within program
   */
  reorder: async (
    courseId: number,
    data: ReorderCourseRequest
  ): Promise<Course> => {
    const response = await apiClient.put<Course>(
      `${COURSES_BASE_URL}/${courseId}/reorder`,
      data
    );
    return response.data;
  },

  /**
   * Get course statistics
   */
  getStatistics: async (programId?: number): Promise<CourseStatistics> => {
    const params = programId ? `?program_id=${programId}` : '';
    const response = await apiClient.get<CourseStatistics>(
      `${COURSES_BASE_URL}/statistics${params}`
    );
    return response.data;
  },
};

export default coursesApi;
