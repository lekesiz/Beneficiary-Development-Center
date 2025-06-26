import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';

import { FileUpload } from '@/components/ui/FileUpload';
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
  useBeneficiaryDocumentUpload,
  useFilesByEntity,
  useDeleteFile,
} from '@/hooks/useFiles';
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
  const { t } = useTranslation();
  const isEditMode = !!id;

  // Queries and mutations
  const { data: beneficiaryData, isLoading: isLoadingBeneficiary } =
    useBeneficiary(Number(id), isEditMode);
  const createMutation = useCreateBeneficiary();
  const updateMutation = useUpdateBeneficiary();
  const documentUpload = useBeneficiaryDocumentUpload();
  const deleteFile = useDeleteFile();

  // File queries
  const { data: beneficiaryDocuments = [] } = useFilesByEntity(
    'beneficiary_document',
    id || ''
  );

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

  // File upload handlers
  const handleDocumentUpload = async (files: File[]) => {
    if (!id) return [];
    
    const results = [];
    for (const file of files) {
      try {
        const result = await documentUpload.mutateAsync({
          file,
          beneficiaryId: id,
        });
        results.push({
          id: result.id,
          name: result.originalName,
          size: result.size,
          type: result.mimetype,
          url: result.url,
        });
      } catch (error) {
        console.error('Failed to upload document:', error);
        results.push({
          id: `error-${Date.now()}`,
          name: file.name,
          size: file.size,
          type: file.type,
          error: 'Upload failed',
        });
      }
    }
    return results;
  };

  const handleFileRemove = async (fileId: string) => {
    try {
      await deleteFile.mutateAsync(fileId);
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  };

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
            {t('beneficiaries.form.backToBeneficiaries')}
          </button>

          <h1 className="text-2xl font-bold">
            {isEditMode ? t('beneficiaries.form.editBeneficiary') : t('beneficiaries.form.addNewBeneficiary')}
          </h1>
          <p className="text-muted-foreground">
            {isEditMode
              ? t('beneficiaries.form.updateDescription')
              : t('beneficiaries.form.createDescription')}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Basic Information */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">{t('beneficiaries.form.sections.basicInfo')}</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label={t('beneficiaries.form.fields.firstName')}
                required
                error={errors.first_name?.message}
              >
                <Input
                  {...register('first_name')}
                  error={!!errors.first_name}
                  placeholder={t('beneficiaries.form.placeholders.firstName')}
                />
              </FormField>

              <FormField
                label={t('beneficiaries.form.fields.lastName')}
                required
                error={errors.last_name?.message}
              >
                <Input
                  {...register('last_name')}
                  error={!!errors.last_name}
                  placeholder={t('beneficiaries.form.placeholders.lastName')}
                />
              </FormField>

              <FormField label={t('beneficiaries.form.fields.email')} error={errors.email?.message}>
                <Input
                  {...register('email')}
                  type="email"
                  error={!!errors.email}
                  placeholder={t('beneficiaries.form.placeholders.email')}
                />
              </FormField>

              <FormField label={t('beneficiaries.form.fields.phone')} error={errors.phone?.message}>
                <Input
                  {...register('phone')}
                  error={!!errors.phone}
                  placeholder={t('beneficiaries.form.placeholders.phone')}
                />
              </FormField>

              <FormField
                label={t('beneficiaries.form.fields.mobilePhone')}
                error={errors.mobile_phone?.message}
              >
                <Input
                  {...register('mobile_phone')}
                  error={!!errors.mobile_phone}
                  placeholder={t('beneficiaries.form.placeholders.mobilePhone')}
                />
              </FormField>

              <FormField
                label={t('beneficiaries.form.fields.externalId')}
                error={errors.external_id?.message}
              >
                <Input
                  {...register('external_id')}
                  error={!!errors.external_id}
                  placeholder={t('beneficiaries.form.placeholders.externalId')}
                />
              </FormField>
            </div>
          </div>

          {/* Personal Information */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">{t('beneficiaries.form.sections.personalInfo')}</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label={t('beneficiaries.form.fields.dateOfBirth')}
                error={errors.date_of_birth?.message}
              >
                <Input
                  {...register('date_of_birth')}
                  type="date"
                  error={!!errors.date_of_birth}
                />
              </FormField>

              <FormField label={t('beneficiaries.form.fields.gender')} error={errors.gender?.message}>
                <Select {...register('gender')} error={!!errors.gender}>
                  <option value="">{t('beneficiaries.form.fields.selectGender')}</option>
                  <option value="male">{t('beneficiaries.gender.male')}</option>
                  <option value="female">{t('beneficiaries.gender.female')}</option>
                  <option value="other">{t('beneficiaries.gender.other')}</option>
                </Select>
              </FormField>

              <FormField
                label={t('beneficiaries.form.fields.nationality')}
                error={errors.nationality?.message}
              >
                <Input
                  {...register('nationality')}
                  error={!!errors.nationality}
                  placeholder={t('beneficiaries.form.placeholders.nationality')}
                />
              </FormField>

              <FormField label={t('beneficiaries.form.fields.birthplace')} error={errors.birthplace?.message}>
                <Input
                  {...register('birthplace')}
                  error={!!errors.birthplace}
                  placeholder={t('beneficiaries.form.placeholders.birthplace')}
                />
              </FormField>
            </div>
          </div>

          {/* Address */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">{t('beneficiaries.form.sections.address')}</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label={t('beneficiaries.form.fields.street')}
                error={errors.address?.street?.message}
                className="md:col-span-2"
              >
                <Input
                  {...register('address.street')}
                  error={!!errors.address?.street}
                  placeholder={t('beneficiaries.form.placeholders.street')}
                />
              </FormField>

              <FormField label={t('beneficiaries.form.fields.city')} error={errors.address?.city?.message}>
                <Input
                  {...register('address.city')}
                  error={!!errors.address?.city}
                  placeholder={t('beneficiaries.form.placeholders.city')}
                />
              </FormField>

              <FormField
                label={t('beneficiaries.form.fields.state')}
                error={errors.address?.state?.message}
              >
                <Input
                  {...register('address.state')}
                  error={!!errors.address?.state}
                  placeholder={t('beneficiaries.form.placeholders.state')}
                />
              </FormField>

              <FormField
                label={t('beneficiaries.form.fields.postalCode')}
                error={errors.address?.postal_code?.message}
              >
                <Input
                  {...register('address.postal_code')}
                  error={!!errors.address?.postal_code}
                  placeholder={t('beneficiaries.form.placeholders.postalCode')}
                />
              </FormField>

              <FormField
                label={t('beneficiaries.form.fields.country')}
                error={errors.address?.country?.message}
              >
                <Input
                  {...register('address.country')}
                  error={!!errors.address?.country}
                  placeholder={t('beneficiaries.form.placeholders.country')}
                />
              </FormField>
            </div>
          </div>

          {/* Professional Information */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">
              {t('beneficiaries.form.sections.professionalInfo')}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label={t('beneficiaries.form.fields.employmentStatus')}
                error={errors.employment_status?.message}
              >
                <Select
                  {...register('employment_status')}
                  error={!!errors.employment_status}
                >
                  <option value="">{t('beneficiaries.form.fields.selectStatus')}</option>
                  {Object.values(EmploymentStatus).map((status) => (
                    <option key={status} value={status}>
                      {status.replace(/_/g, ' ').charAt(0).toUpperCase() +
                        status.replace(/_/g, ' ').slice(1)}
                    </option>
                  ))}
                </Select>
              </FormField>

              <FormField label={t('beneficiaries.form.fields.jobTitle')} error={errors.job_title?.message}>
                <Input
                  {...register('job_title')}
                  error={!!errors.job_title}
                  placeholder={t('beneficiaries.form.placeholders.jobTitle')}
                />
              </FormField>

              <FormField label={t('beneficiaries.form.fields.company')} error={errors.company?.message}>
                <Input
                  {...register('company')}
                  error={!!errors.company}
                  placeholder={t('beneficiaries.form.placeholders.company')}
                />
              </FormField>

              <FormField label={t('beneficiaries.form.fields.industry')} error={errors.industry?.message}>
                <Input
                  {...register('industry')}
                  error={!!errors.industry}
                  placeholder={t('beneficiaries.form.placeholders.industry')}
                />
              </FormField>

              <FormField
                label={t('beneficiaries.form.fields.yearsOfExperience')}
                error={errors.years_of_experience?.message}
              >
                <Input
                  {...register('years_of_experience', { valueAsNumber: true })}
                  type="number"
                  min="0"
                  max="70"
                  error={!!errors.years_of_experience}
                  placeholder={t('beneficiaries.form.placeholders.yearsOfExperience')}
                />
              </FormField>
            </div>
          </div>

          {/* Education */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">{t('beneficiaries.form.sections.education')}</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label={t('beneficiaries.form.fields.educationLevel')}
                error={errors.education_level?.message}
              >
                <Select
                  {...register('education_level')}
                  error={!!errors.education_level}
                >
                  <option value="">{t('beneficiaries.form.fields.selectLevel')}</option>
                  {Object.values(EducationLevel).map((level) => (
                    <option key={level} value={level}>
                      {level.replace(/_/g, ' ').charAt(0).toUpperCase() +
                        level.replace(/_/g, ' ').slice(1)}
                    </option>
                  ))}
                </Select>
              </FormField>

              <FormField
                label={t('beneficiaries.form.fields.fieldOfStudy')}
                error={errors.field_of_study?.message}
              >
                <Input
                  {...register('field_of_study')}
                  error={!!errors.field_of_study}
                  placeholder={t('beneficiaries.form.placeholders.fieldOfStudy')}
                />
              </FormField>
            </div>

            <FormField
              label={t('beneficiaries.form.fields.certifications')}
              error={errors.certifications?.message}
            >
              <Controller
                name="certifications"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    placeholder={t('beneficiaries.form.fields.addCertification')}
                    error={!!errors.certifications}
                  />
                )}
              />
            </FormField>
          </div>

          {/* Skills & Interests */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">{t('beneficiaries.form.sections.skillsInterests')}</h2>

            <FormField label={t('beneficiaries.form.fields.skills')} error={errors.skills?.message}>
              <Controller
                name="skills"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    placeholder={t('beneficiaries.form.fields.addSkill')}
                    error={!!errors.skills}
                  />
                )}
              />
            </FormField>

            <FormField label={t('beneficiaries.form.fields.interests')} error={errors.interests?.message}>
              <Controller
                name="interests"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    placeholder={t('beneficiaries.form.fields.addInterest')}
                    error={!!errors.interests}
                  />
                )}
              />
            </FormField>

            <FormField label={t('beneficiaries.form.fields.goals')} error={errors.goals?.message}>
              <Controller
                name="goals"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    placeholder={t('beneficiaries.form.fields.addGoal')}
                    error={!!errors.goals}
                  />
                )}
              />
            </FormField>
          </div>

          {/* Management */}
          <div className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-lg font-semibold mb-4">{t('beneficiaries.form.sections.management')}</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {canEditStatus && (
                <FormField label={t('beneficiaries.form.fields.status')} error={errors.status?.message}>
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
                label={t('beneficiaries.form.fields.tags')}
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
                      placeholder={t('beneficiaries.form.fields.addTag')}
                      error={!!errors.tags}
                    />
                  )}
                />
              </FormField>
            </div>
          </div>

          {/* Documents */}
          {isEditMode && id && (
            <div className="bg-white p-6 rounded-lg shadow space-y-4">
              <h2 className="text-lg font-semibold mb-4">Documents</h2>
              <p className="text-sm text-gray-600 mb-4">
                Upload identification documents, certificates, CVs, and other relevant files.
              </p>
              <FileUpload
                onUpload={handleDocumentUpload}
                onRemove={handleFileRemove}
                maxFiles={15}
                maxSize={20 * 1024 * 1024} // 20MB
                acceptedTypes={[
                  'application/pdf',
                  'application/msword',
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                  'image/jpeg',
                  'image/png',
                  'image/jpg',
                  'text/plain',
                ]}
                uploadedFiles={beneficiaryDocuments.map(file => ({
                  id: file.id,
                  name: file.name,
                  size: file.size,
                  type: file.type,
                  url: file.url,
                }))}
                className="w-full"
              />
            </div>
          )}

          {!isEditMode && (
            <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
              <div className="flex items-start space-x-3">
                <div className="text-blue-600 text-sm">ℹ️</div>
                <div>
                  <h4 className="font-medium text-blue-900 mb-1">{t('beneficiaries.form.documents.uploadNote')}</h4>
                  <p className="text-sm text-blue-700">
                    {t('beneficiaries.form.documents.uploadNoteDescription')}
                  </p>
                </div>
              </div>
            </div>
          )}

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
