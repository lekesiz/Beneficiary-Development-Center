import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import * as React from 'react';
import { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';

import {
  FormField,
  Input,
  Select,
  Textarea,
  Button,
} from '@/components/ui/Form';
import { TagInput } from '@/components/ui/TagInput';
import { useAuth } from '@/contexts/AuthContext';
import {
  useBeneficiary,
  useCreateBeneficiary,
  useUpdateBeneficiary,
} from '@/hooks/useBeneficiaries';
import {
  beneficiaryFormSchema,
  BeneficiaryFormData,
  transformFormDataForAPI,
} from '@/schemas/beneficiary';
import {
  BeneficiaryStatus,
  EmploymentStatus,
  EducationLevel,
} from '@/types/beneficiary';

export default function BeneficiaryForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { user } = useAuth();
  const isEditMode = !!id;

  // Queries and mutations
  const { data: beneficiaryData, isLoading: isLoadingBeneficiary } =
    useBeneficiary(Number(id), isEditMode);
  const createMutation = useCreateBeneficiary();
  const updateMutation = useUpdateBeneficiary();

  // Form setup
  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<BeneficiaryFormData>({
    resolver: zodResolver(beneficiaryFormSchema),
    defaultValues: {
      status: BeneficiaryStatus.ACTIVE,
      address: {
        country: 'France',
      },
      certifications: [],
      skills: [],
      interests: [],
      goals: [],
      tags: [],
    },
  });

  // Load existing data in edit mode
  useEffect(() => {
    if (isEditMode && beneficiaryData?.data.beneficiary) {
      const beneficiary = beneficiaryData.data.beneficiary;
      reset({
        first_name: beneficiary.first_name,
        last_name: beneficiary.last_name,
        email: beneficiary.email || '',
        phone: beneficiary.phone || '',
        mobile_phone: beneficiary.mobile_phone || '',
        date_of_birth: beneficiary.date_of_birth || '',
        gender: beneficiary.gender as any,
        nationality: beneficiary.nationality || '',
        birthplace: beneficiary.birthplace || '',
        address: beneficiary.address,
        employment_status: beneficiary.employment_status,
        job_title: beneficiary.job_title || '',
        company: beneficiary.company || '',
        industry: beneficiary.industry || '',
        years_of_experience: beneficiary.years_of_experience,
        education_level: beneficiary.education_level,
        field_of_study: beneficiary.field_of_study || '',
        certifications: beneficiary.certifications,
        skills: beneficiary.skills,
        interests: beneficiary.interests,
        goals: beneficiary.goals,
        tags: beneficiary.tags,
        status: beneficiary.status,
        external_id: beneficiary.external_id || '',
        assigned_trainer_id: beneficiary.assigned_trainer_id,
      });
    }
  }, [isEditMode, beneficiaryData, reset]);

  const onSubmit = async (data: BeneficiaryFormData) => {
    const transformedData = transformFormDataForAPI(data);

    try {
      if (isEditMode) {
        await updateMutation.mutateAsync({
          id: Number(id),
          data: transformedData,
        });
      } else {
        await createMutation.mutateAsync(transformedData);
      }
      navigate('/beneficiaries');
    } catch (error) {
      // Error is handled by the mutation
    }
  };

  if (isEditMode && isLoadingBeneficiary) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  const canEditStatus = user?.role === 'admin' || user?.role === 'super_admin';

  return (
    <div className="container mx-auto py-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/beneficiaries')}
            className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Beneficiaries
          </button>

          <h1 className="text-2xl font-bold">
            {isEditMode ? 'Edit Beneficiary' : 'Add New Beneficiary'}
          </h1>
          <p className="text-muted-foreground">
            {isEditMode
              ? 'Update beneficiary information'
              : 'Create a new beneficiary profile'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Basic Information */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">Basic Information</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label="First Name"
                required
                error={errors.first_name?.message}
              >
                <Input
                  {...register('first_name')}
                  error={!!errors.first_name}
                  placeholder="John"
                />
              </FormField>

              <FormField
                label="Last Name"
                required
                error={errors.last_name?.message}
              >
                <Input
                  {...register('last_name')}
                  error={!!errors.last_name}
                  placeholder="Doe"
                />
              </FormField>

              <FormField label="Email" error={errors.email?.message}>
                <Input
                  {...register('email')}
                  type="email"
                  error={!!errors.email}
                  placeholder="john.doe@example.com"
                />
              </FormField>

              <FormField label="Phone" error={errors.phone?.message}>
                <Input
                  {...register('phone')}
                  error={!!errors.phone}
                  placeholder="+33 1 23 45 67 89"
                />
              </FormField>

              <FormField
                label="Mobile Phone"
                error={errors.mobile_phone?.message}
              >
                <Input
                  {...register('mobile_phone')}
                  error={!!errors.mobile_phone}
                  placeholder="+33 6 12 34 56 78"
                />
              </FormField>

              <FormField
                label="External ID"
                error={errors.external_id?.message}
              >
                <Input
                  {...register('external_id')}
                  error={!!errors.external_id}
                  placeholder="External system ID"
                />
              </FormField>
            </div>
          </div>

          {/* Personal Information */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">Personal Information</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label="Date of Birth"
                error={errors.date_of_birth?.message}
              >
                <Input
                  {...register('date_of_birth')}
                  type="date"
                  error={!!errors.date_of_birth}
                />
              </FormField>

              <FormField label="Gender" error={errors.gender?.message}>
                <Select {...register('gender')} error={!!errors.gender}>
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </Select>
              </FormField>

              <FormField
                label="Nationality"
                error={errors.nationality?.message}
              >
                <Input
                  {...register('nationality')}
                  error={!!errors.nationality}
                  placeholder="French"
                />
              </FormField>

              <FormField label="Birthplace" error={errors.birthplace?.message}>
                <Input
                  {...register('birthplace')}
                  error={!!errors.birthplace}
                  placeholder="Paris, France"
                />
              </FormField>
            </div>
          </div>

          {/* Address */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">Address</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label="Street"
                error={errors.address?.street?.message}
                className="md:col-span-2"
              >
                <Input
                  {...register('address.street')}
                  error={!!errors.address?.street}
                  placeholder="123 Main Street"
                />
              </FormField>

              <FormField label="City" error={errors.address?.city?.message}>
                <Input
                  {...register('address.city')}
                  error={!!errors.address?.city}
                  placeholder="Paris"
                />
              </FormField>

              <FormField
                label="State/Region"
                error={errors.address?.state?.message}
              >
                <Input
                  {...register('address.state')}
                  error={!!errors.address?.state}
                  placeholder="Île-de-France"
                />
              </FormField>

              <FormField
                label="Postal Code"
                error={errors.address?.postal_code?.message}
              >
                <Input
                  {...register('address.postal_code')}
                  error={!!errors.address?.postal_code}
                  placeholder="75001"
                />
              </FormField>

              <FormField
                label="Country"
                error={errors.address?.country?.message}
              >
                <Input
                  {...register('address.country')}
                  error={!!errors.address?.country}
                  placeholder="France"
                />
              </FormField>
            </div>
          </div>

          {/* Professional Information */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">
              Professional Information
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label="Employment Status"
                error={errors.employment_status?.message}
              >
                <Select
                  {...register('employment_status')}
                  error={!!errors.employment_status}
                >
                  <option value="">Select status</option>
                  {Object.values(EmploymentStatus).map((status) => (
                    <option key={status} value={status}>
                      {status.replace(/_/g, ' ').charAt(0).toUpperCase() +
                        status.replace(/_/g, ' ').slice(1)}
                    </option>
                  ))}
                </Select>
              </FormField>

              <FormField label="Job Title" error={errors.job_title?.message}>
                <Input
                  {...register('job_title')}
                  error={!!errors.job_title}
                  placeholder="Software Developer"
                />
              </FormField>

              <FormField label="Company" error={errors.company?.message}>
                <Input
                  {...register('company')}
                  error={!!errors.company}
                  placeholder="Tech Corp"
                />
              </FormField>

              <FormField label="Industry" error={errors.industry?.message}>
                <Input
                  {...register('industry')}
                  error={!!errors.industry}
                  placeholder="Technology"
                />
              </FormField>

              <FormField
                label="Years of Experience"
                error={errors.years_of_experience?.message}
              >
                <Input
                  {...register('years_of_experience', { valueAsNumber: true })}
                  type="number"
                  min="0"
                  max="70"
                  error={!!errors.years_of_experience}
                  placeholder="5"
                />
              </FormField>
            </div>
          </div>

          {/* Education */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">Education</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label="Education Level"
                error={errors.education_level?.message}
              >
                <Select
                  {...register('education_level')}
                  error={!!errors.education_level}
                >
                  <option value="">Select level</option>
                  {Object.values(EducationLevel).map((level) => (
                    <option key={level} value={level}>
                      {level.replace(/_/g, ' ').charAt(0).toUpperCase() +
                        level.replace(/_/g, ' ').slice(1)}
                    </option>
                  ))}
                </Select>
              </FormField>

              <FormField
                label="Field of Study"
                error={errors.field_of_study?.message}
              >
                <Input
                  {...register('field_of_study')}
                  error={!!errors.field_of_study}
                  placeholder="Computer Science"
                />
              </FormField>
            </div>

            <FormField
              label="Certifications"
              error={errors.certifications?.message}
            >
              <Controller
                name="certifications"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    placeholder="Add certification..."
                    error={!!errors.certifications}
                  />
                )}
              />
            </FormField>
          </div>

          {/* Skills & Interests */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">Skills & Interests</h2>

            <FormField label="Skills" error={errors.skills?.message}>
              <Controller
                name="skills"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    placeholder="Add skill..."
                    error={!!errors.skills}
                  />
                )}
              />
            </FormField>

            <FormField label="Interests" error={errors.interests?.message}>
              <Controller
                name="interests"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    placeholder="Add interest..."
                    error={!!errors.interests}
                  />
                )}
              />
            </FormField>

            <FormField label="Goals" error={errors.goals?.message}>
              <Controller
                name="goals"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    placeholder="Add goal..."
                    error={!!errors.goals}
                  />
                )}
              />
            </FormField>
          </div>

          {/* Management */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">Management</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {canEditStatus && (
                <FormField label="Status" error={errors.status?.message}>
                  <Select {...register('status')} error={!!errors.status}>
                    {Object.values(BeneficiaryStatus).map((status) => (
                      <option key={status} value={status}>
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                      </option>
                    ))}
                  </Select>
                </FormField>
              )}

              <FormField
                label="Tags"
                error={errors.tags?.message}
                className={canEditStatus ? '' : 'md:col-span-2'}
              >
                <Controller
                  name="tags"
                  control={control}
                  render={({ field }) => (
                    <TagInput
                      value={field.value}
                      onChange={field.onChange}
                      placeholder="Add tag..."
                      error={!!errors.tags}
                    />
                  )}
                />
              </FormField>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/beneficiaries')}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              loading={
                isSubmitting ||
                createMutation.isPending ||
                updateMutation.isPending
              }
            >
              <Save className="h-4 w-4 mr-2" />
              {isEditMode ? 'Update Beneficiary' : 'Create Beneficiary'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
