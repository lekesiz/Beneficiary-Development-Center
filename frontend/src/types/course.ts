/**
 * Course related types and interfaces
 */

export enum CourseStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
}

export enum CourseFormat {
  LECTURE = 'lecture',
  WORKSHOP = 'workshop',
  PRACTICAL = 'practical',
  ONLINE = 'online',
  SELF_PACED = 'self_paced',
  HYBRID = 'hybrid',
}

export enum DifficultyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert',
}

export interface Course {
  id: number;
  uuid: string;
  code: string;
  title: string;
  subtitle?: string;
  description?: string;
  program_id: number;
  status: CourseStatus;
  format: CourseFormat;
  difficulty_level: DifficultyLevel;
  duration_hours: number;
  duration_weeks?: number;
  order_index: number;
  objectives: string[];
  outline: any[];
  prerequisites: string[];
  materials: string[];
  content_url?: string;
  video_url?: string;
  resources: any[];
  assignments: any[];
  has_assessment: boolean;
  assessment_type?: string;
  passing_score?: number;
  max_attempts?: number;
  min_participants: number;
  max_participants?: number;
  tags: string[];
  course_metadata: Record<string, any>;
  thumbnail_url?: string;
  instructor_id?: number;
  created_by: number;
  created_at: string;
  updated_at: string;

  // Computed fields
  total_duration_hours: number;
  is_available: boolean;

  // Related data (when include_related=true)
  participant_count?: number;
  available_spots?: number;
  completion_rate?: number;
  average_score?: number;
  session_count?: number;
  instructor_name?: string;
  program_title?: string;
  program_code?: string;
  sessions?: CourseSession[];
}

export interface CourseSession {
  id: number;
  uuid: string;
  course_id: number;
  title: string;
  description?: string;
  session_date: string;
  duration_hours: number;
  location?: string;
  room_number?: string;
  is_online: boolean;
  online_link?: string;
  instructor_id?: number;
  is_mandatory: boolean;
  is_cancelled: boolean;
  cancellation_reason?: string;
  materials_url?: string;
  recording_url?: string;
  created_at: string;
  updated_at: string;

  // Computed fields
  end_time?: string;

  // Related data
  instructor_name?: string;
  attendance_count?: number;
}

export interface CreateCourseRequest {
  program_id: number;
  title: string;
  subtitle?: string;
  description?: string;
  status?: CourseStatus;
  format?: CourseFormat;
  difficulty_level?: DifficultyLevel;
  duration_hours?: number;
  duration_weeks?: number;
  order_index?: number;
  objectives?: string[];
  outline?: any[];
  prerequisites?: string[];
  materials?: string[];
  content_url?: string;
  video_url?: string;
  resources?: any[];
  assignments?: any[];
  has_assessment?: boolean;
  assessment_type?: string;
  passing_score?: number;
  max_attempts?: number;
  min_participants?: number;
  max_participants?: number;
  tags?: string[];
  course_metadata?: Record<string, any>;
  thumbnail_url?: string;
  instructor_id?: number;
}

export type UpdateCourseRequest = Partial<Omit<CreateCourseRequest, 'program_id'>>

export interface CourseFilters {
  page?: number;
  per_page?: number;
  program_id?: number;
  status?: CourseStatus;
  format?: CourseFormat;
  difficulty?: DifficultyLevel;
  search?: string;
  instructor_id?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface CoursesResponse {
  courses: Course[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface CreateSessionRequest {
  title: string;
  description?: string;
  session_date: string;
  duration_hours?: number;
  location?: string;
  room_number?: string;
  is_online?: boolean;
  online_link?: string;
  instructor_id?: number;
  is_mandatory?: boolean;
  materials_url?: string;
}

export interface DuplicateCourseRequest {
  target_program_id?: number;
}

export interface ReorderCourseRequest {
  order_index: number;
}

export interface CourseStatistics {
  total_courses: number;
  status_breakdown: Record<string, number>;
  format_breakdown: Record<string, number>;
  difficulty_breakdown: Record<string, number>;
  courses_with_assessment: number;
  average_completion_rate: number;
  average_assessment_score?: number;
  total_sessions: number;
}
