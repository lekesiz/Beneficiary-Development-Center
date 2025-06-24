/**
 * Programs API client
 */
import { apiClient } from './client';
import type {
  Program,
  CreateProgramRequest,
  UpdateProgramRequest,
  ProgramFilters,
  ProgramsResponse,
  ProgramStatistics,
  CreateCourseInProgramRequest
} from '../types/program';
import type { Course } from '../types/course';

const PROGRAMS_BASE_URL = '/programs';

export const programsApi = {
  /**
   * Get all programs with optional filters
   */
  getAll: async (filters?: ProgramFilters): Promise<ProgramsResponse> => {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    
    const response = await apiClient.get<ProgramsResponse>(
      `${PROGRAMS_BASE_URL}?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get program by ID
   */
  getById: async (id: number, includeCourses = false): Promise<Program> => {
    const params = includeCourses ? '?include_courses=true' : '';
    const response = await apiClient.get<Program>(`${PROGRAMS_BASE_URL}/${id}${params}`);
    return response.data;
  },

  /**
   * Create new program
   */
  create: async (data: CreateProgramRequest): Promise<Program> => {
    const response = await apiClient.post<Program>(PROGRAMS_BASE_URL, data);
    return response.data;
  },

  /**
   * Update program
   */
  update: async (id: number, data: UpdateProgramRequest): Promise<Program> => {
    const response = await apiClient.put<Program>(`${PROGRAMS_BASE_URL}/${id}`, data);
    return response.data;
  },

  /**
   * Delete program
   */
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`${PROGRAMS_BASE_URL}/${id}`);
  },

  /**
   * Update program status
   */
  updateStatus: async (id: number, status: string): Promise<Program> => {
    const response = await apiClient.put<Program>(
      `${PROGRAMS_BASE_URL}/${id}/status`,
      { status }
    );
    return response.data;
  },

  /**
   * Add course to program
   */
  addCourse: async (programId: number, courseData: CreateCourseInProgramRequest): Promise<Course> => {
    const response = await apiClient.post<Course>(
      `${PROGRAMS_BASE_URL}/${programId}/courses`,
      courseData
    );
    return response.data;
  },

  /**
   * Get program statistics
   */
  getStatistics: async (): Promise<ProgramStatistics> => {
    const response = await apiClient.get<ProgramStatistics>(`${PROGRAMS_BASE_URL}/statistics`);
    return response.data;
  }
};

export default programsApi;