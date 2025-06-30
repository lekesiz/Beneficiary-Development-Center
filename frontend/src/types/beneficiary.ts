export enum BeneficiaryStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  COMPLETED = 'completed',
  SUSPENDED = 'suspended',
}

export enum EmploymentStatus {
  EMPLOYED = 'employed',
  UNEMPLOYED = 'unemployed',
  STUDENT = 'student',
  SELF_EMPLOYED = 'self_employed',
  RETIRED = 'retired',
  OTHER = 'other',
}

export enum EducationLevel {
  NO_DIPLOMA = 'no_diploma',
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  HIGH_SCHOOL = 'high_school',
  BACHELOR = 'bachelor',
  MASTER = 'master',
  DOCTORATE = 'doctorate',
  OTHER = 'other',
}

export interface Address {
  street: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

export interface Note {
  id: string;
  text: string;
  created_by: number;
  created_at: string;
}

export interface ProfileData {
  emergency_contact: Record<string, any>;
  languages: string[];
  availability: Record<string, any>;
  preferences: Record<string, any>;
  custom_fields: Record<string, any>;
}

export interface ProgressSummary {
  overall_progress: number;
  enrollments: Array<{
    program_id: number;
    program_name: string;
    progress: number;
    status: string;
  }>;
}

export interface Beneficiary {
  id: number;
  uuid: string;
  external_id?: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email?: string;
  phone?: string;
  mobile_phone?: string;

  // Personal information
  date_of_birth?: string;
  age?: number;
  gender?: string;
  nationality?: string;
  birthplace?: string;

  // Address
  address: Address;

  // Professional information
  employment_status?: EmploymentStatus;
  job_title?: string;
  company?: string;
  industry?: string;
  years_of_experience?: number;

  // Education
  education_level?: EducationLevel;
  field_of_study?: string;
  certifications: string[];

  // Profile data
  profile_data: ProfileData;
  skills: string[];
  interests: string[];
  goals: string[];

  // Status and management
  status: BeneficiaryStatus;
  notes: Note[];
  tags: string[];

  // Relationships
  created_by: number;
  assigned_trainer_id?: number;
  assigned_trainer_name?: string;

  // Related data
  progress_summary?: ProgressSummary;
  active_enrollments?: number;
  completed_programs?: number;

  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface BeneficiaryCreate {
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  mobile_phone?: string;
  date_of_birth?: string;
  gender?: string;
  nationality?: string;
  birthplace?: string;
  address?: Partial<Address>;
  employment_status?: EmploymentStatus;
  job_title?: string;
  company?: string;
  industry?: string;
  years_of_experience?: number;
  education_level?: EducationLevel;
  field_of_study?: string;
  certifications?: string[];
  profile_data?: Partial<ProfileData>;
  skills?: string[];
  interests?: string[];
  goals?: string[];
  status?: BeneficiaryStatus;
  external_id?: string;
  assigned_trainer_id?: number;
  tags?: string[];
}

export type BeneficiaryUpdate = Partial<BeneficiaryCreate>;

export interface BeneficiaryListParams {
  page?: number;
  per_page?: number;
  search?: string;
  status?: BeneficiaryStatus;
  assigned_trainer_id?: number;
  tags?: string[];
  sort_by?: 'created_at' | 'updated_at' | 'first_name' | 'last_name' | 'email';
  sort_order?: 'asc' | 'desc';
}

export interface Pagination {
  page: number;
  per_page: number;
  total: number;
  pages: number;
}

export interface BeneficiaryListResponse {
  beneficiaries: Beneficiary[];
  pagination: Pagination;
}

export interface BeneficiaryStatistics {
  total: number;
  by_status: Record<string, number>;
  by_employment: Record<string, number>;
  by_education: Record<string, number>;
  by_age: Record<string, number>;
}
