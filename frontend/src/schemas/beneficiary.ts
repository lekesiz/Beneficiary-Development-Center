import { z } from 'zod'
import { BeneficiaryStatus, EmploymentStatus, EducationLevel } from '@/types/beneficiary'

export const addressSchema = z.object({
  street: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  postal_code: z.string().optional(),
  country: z.string().default('France'),
})

export const beneficiaryFormSchema = z.object({
  // Required fields
  first_name: z.string()
    .min(2, 'First name must be at least 2 characters')
    .max(50, 'First name must be less than 50 characters'),
  
  last_name: z.string()
    .min(2, 'Last name must be at least 2 characters')
    .max(50, 'Last name must be less than 50 characters'),
  
  // Contact information
  email: z.string()
    .email('Invalid email address')
    .optional()
    .or(z.literal('')),
  
  phone: z.string()
    .regex(/^\+?[\d\s\-\(\)]+$/, 'Invalid phone number format')
    .optional()
    .or(z.literal('')),
  
  mobile_phone: z.string()
    .regex(/^\+?[\d\s\-\(\)]+$/, 'Invalid mobile phone format')
    .optional()
    .or(z.literal('')),
  
  // Personal information
  date_of_birth: z.string().optional().or(z.literal('')),
  
  gender: z.enum(['male', 'female', 'other']).optional(),
  
  nationality: z.string()
    .max(50, 'Nationality must be less than 50 characters')
    .optional()
    .or(z.literal('')),
  
  birthplace: z.string()
    .max(100, 'Birthplace must be less than 100 characters')
    .optional()
    .or(z.literal('')),
  
  // Address
  address: addressSchema.optional(),
  
  // Professional information
  employment_status: z.nativeEnum(EmploymentStatus).optional(),
  
  job_title: z.string()
    .max(100, 'Job title must be less than 100 characters')
    .optional()
    .or(z.literal('')),
  
  company: z.string()
    .max(100, 'Company must be less than 100 characters')
    .optional()
    .or(z.literal('')),
  
  industry: z.string()
    .max(100, 'Industry must be less than 100 characters')
    .optional()
    .or(z.literal('')),
  
  years_of_experience: z.number()
    .min(0, 'Years of experience cannot be negative')
    .max(70, 'Years of experience seems too high')
    .optional()
    .or(z.nan()),
  
  // Education
  education_level: z.nativeEnum(EducationLevel).optional(),
  
  field_of_study: z.string()
    .max(100, 'Field of study must be less than 100 characters')
    .optional()
    .or(z.literal('')),
  
  // Arrays
  certifications: z.array(z.string()).default([]),
  skills: z.array(z.string()).default([]),
  interests: z.array(z.string()).default([]),
  goals: z.array(z.string()).default([]),
  tags: z.array(z.string()).default([]),
  
  // Status and management
  status: z.nativeEnum(BeneficiaryStatus).default(BeneficiaryStatus.ACTIVE),
  
  external_id: z.string()
    .max(100, 'External ID must be less than 100 characters')
    .optional()
    .or(z.literal('')),
  
  assigned_trainer_id: z.number().optional().nullable(),
})

export type BeneficiaryFormData = z.infer<typeof beneficiaryFormSchema>

// Helper to transform form data for API
export const transformFormDataForAPI = (data: BeneficiaryFormData) => {
  const transformed: any = { ...data }
  
  // Convert empty strings to null/undefined
  Object.keys(transformed).forEach(key => {
    if (transformed[key] === '') {
      transformed[key] = undefined
    }
  })
  
  // Convert NaN to undefined for years_of_experience
  if (isNaN(transformed.years_of_experience)) {
    transformed.years_of_experience = undefined
  }
  
  // Ensure address has proper structure
  if (transformed.address) {
    transformed.address = {
      street: transformed.address.street || '',
      city: transformed.address.city || '',
      state: transformed.address.state || '',
      postal_code: transformed.address.postal_code || '',
      country: transformed.address.country || 'France',
    }
  }
  
  return transformed
}