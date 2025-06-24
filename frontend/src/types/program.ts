/**
 * Program related types and interfaces
 */

export enum ProgramStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}

export enum ProgramType {
  TRAINING = 'training',
  WORKSHOP = 'workshop',
  CERTIFICATION = 'certification',
  BOOTCAMP = 'bootcamp',
  MENTORSHIP = 'mentorship',
  OTHER = 'other'
}

export interface Program {
  id: number;
  uuid: string;
  code: string;
  title: string;
  description?: string;
  objectives: string[];
  program_type: ProgramType;
  status: ProgramStatus;
  start_date: string;
  end_date: string;
  enrollment_start?: string;
  enrollment_end?: string;
  min_participants: number;
  max_participants: number;
  requirements: Record<string, any>;
  location?: string;
  is_online: boolean;
  is_hybrid: boolean;
  online_link?: string;
  price: number;
  currency: string;
  tags: string[];
  program_metadata: Record<string, any>;
  cover_image_url?: string;
  resources: any[];
  created_by: number;
  coordinator_id?: number;
  created_at: string;
  updated_at: string;
  
  // Computed fields
  duration_days: number;
  is_enrollment_open: boolean;
  is_active: boolean;
  is_upcoming: boolean;
  is_past: boolean;
  
  // Related data (when include_related=true)
  enrollment_count?: number;
  available_spots?: number;
  completion_rate?: number;
  course_count?: number;
  coordinator_name?: string;
  courses?: any[]; // Will be populated when needed
}

export interface CreateProgramRequest {
  title: string;
  description?: string;
  objectives?: string[];
  program_type?: ProgramType;
  start_date: string;
  end_date: string;
  enrollment_start?: string;
  enrollment_end?: string;
  min_participants?: number;
  max_participants?: number;
  requirements?: Record<string, any>;
  location?: string;
  is_online?: boolean;
  is_hybrid?: boolean;
  online_link?: string;
  price?: number;
  currency?: string;
  tags?: string[];
  program_metadata?: Record<string, any>;
  cover_image_url?: string;
  resources?: any[];
  coordinator_id?: number;
}

export interface UpdateProgramRequest extends Partial<CreateProgramRequest> {}

export interface ProgramFilters {
  page?: number;
  per_page?: number;
  status?: ProgramStatus;
  type?: ProgramType;
  search?: string;
  upcoming_only?: boolean;
  active_only?: boolean;
}

export interface ProgramsResponse {
  programs: Program[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface ProgramStatistics {
  total_programs: number;
  status_breakdown: Record<string, number>;
  type_breakdown: Record<string, number>;
  upcoming_programs: number;
  active_programs: number;
  total_active_enrollments: number;
}

export interface CreateCourseInProgramRequest {
  title: string;
  subtitle?: string;
  description?: string;
  format?: string;
  difficulty_level?: string;
  duration_hours?: number;
  objectives?: string[];
  instructor_id?: number;
}