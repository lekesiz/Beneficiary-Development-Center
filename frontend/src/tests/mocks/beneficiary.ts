import {
  Beneficiary,
  BeneficiaryStatus,
  EmploymentStatus,
  EducationLevel,
} from '@/types/beneficiary';

export const mockBeneficiary: Beneficiary = {
  id: 1,
  uuid: '123e4567-e89b-12d3-a456-426614174000',
  external_id: 'EXT001',
  first_name: 'John',
  last_name: 'Doe',
  full_name: 'John Doe',
  email: 'john.doe@example.com',
  phone: '+33123456789',
  mobile_phone: '+33612345678',

  // Personal information
  date_of_birth: '1990-01-01',
  age: 34,
  gender: 'male',
  nationality: 'French',
  birthplace: 'Paris, France',

  // Address
  address: {
    street: '123 Main Street',
    city: 'Paris',
    state: 'Île-de-France',
    postal_code: '75001',
    country: 'France',
  },

  // Professional information
  employment_status: EmploymentStatus.EMPLOYED,
  job_title: 'Software Developer',
  company: 'Tech Corp',
  industry: 'Technology',
  years_of_experience: 5,

  // Education
  education_level: EducationLevel.BACHELOR,
  field_of_study: 'Computer Science',
  certifications: ['AWS Certified', 'Scrum Master'],

  // Profile data
  profile_data: {
    emergency_contact: { name: 'Jane Doe', phone: '+33123456789' },
    languages: ['French', 'English'],
    availability: { monday: true, tuesday: true },
    preferences: { remote: true },
    custom_fields: {},
  },
  skills: ['JavaScript', 'React', 'Node.js'],
  interests: ['Web Development', 'AI', 'Open Source'],
  goals: ['Learn Machine Learning', 'Start a tech startup'],

  // Status and management
  status: BeneficiaryStatus.ACTIVE,
  notes: [
    {
      id: '1',
      text: 'Initial assessment completed',
      created_by: 1,
      created_at: '2024-01-01T10:00:00Z',
    },
  ],
  tags: ['developer', 'remote', 'experienced'],

  // Relationships
  created_by: 1,
  assigned_trainer_id: 2,
  assigned_trainer_name: 'Jane Trainer',

  // Related data
  progress_summary: {
    overall_progress: 75,
    enrollments: [
      {
        program_id: 1,
        program_name: 'Web Development',
        progress: 80,
        status: 'in_progress',
      },
      {
        program_id: 2,
        program_name: 'React Advanced',
        progress: 70,
        status: 'in_progress',
      },
    ],
  },
  active_enrollments: 2,
  completed_programs: 1,

  // Timestamps
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z',
};

export const mockBeneficiaryList = [
  mockBeneficiary,
  {
    ...mockBeneficiary,
    id: 2,
    uuid: '223e4567-e89b-12d3-a456-426614174001',
    first_name: 'Jane',
    last_name: 'Smith',
    full_name: 'Jane Smith',
    email: 'jane.smith@example.com',
    status: BeneficiaryStatus.INACTIVE,
    tags: ['designer', 'freelance'],
  },
  {
    ...mockBeneficiary,
    id: 3,
    uuid: '323e4567-e89b-12d3-a456-426614174002',
    first_name: 'Bob',
    last_name: 'Johnson',
    full_name: 'Bob Johnson',
    email: 'bob.johnson@example.com',
    status: BeneficiaryStatus.COMPLETED,
    assigned_trainer_id: undefined,
    assigned_trainer_name: undefined,
  },
];

export const createMockBeneficiary = (
  overrides?: Partial<Beneficiary>
): Beneficiary => {
  return {
    ...mockBeneficiary,
    ...overrides,
  };
};
