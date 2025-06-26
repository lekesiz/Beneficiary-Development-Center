/**
 * Program Form Page (Create/Edit)
 */
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft, Save, X, Plus } from 'lucide-react';
import * as React from 'react';
import { useEffect, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate } from 'react-router-dom';
import { z } from 'zod';

import { FormSkeleton } from '../../components/common/FormSkeleton';
import { Autocomplete } from '../../components/ui/Autocomplete';
import { Badge } from '../../components/ui/Badge';
import { Card } from '../../components/ui/Card';
import { DatePicker } from '../../components/ui/DatePicker';
import { Button, Select, Textarea } from '../../components/ui/Form';
import { Input } from '../../components/ui/Input';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import {
  PROGRAM_STATUS_OPTIONS,
  PROGRAM_TYPE_OPTIONS,
} from '../../constants/program';
import { useAuth } from '../../contexts/AuthContext';
import {
  useProgram,
  useCreateProgram,
  useUpdateProgram,
} from '../../hooks/usePrograms';
import { programFormSchema, type ProgramFormData } from '../../schemas/programForm';
import { ProgramType, ProgramStatus } from '../../types/program';
import type {
  CreateProgramRequest,
  UpdateProgramRequest,
} from '../../types/program';


// Remove the duplicate schema definition as we're importing it from schemas/program.ts

export const ProgramForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { t } = useTranslation();
  const isEdit = !!id;
  const programId = isEdit ? parseInt(id!) : null;

  // Fetch program data for edit
  const { data: programResponse, isLoading: isLoadingProgram } = useProgram(
    programId!,
    !!programId
  );
  const program = programResponse?.program;

  // Mutations
  const createProgram = useCreateProgram();
  const updateProgram = useUpdateProgram();

  // State
  const [objectives, setObjectives] = useState<string[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [newObjective, setNewObjective] = useState('');
  const [newTag, setNewTag] = useState('');

  // Permission checks
  const canEdit = user?.role && ['admin', 'manager'].includes(user.role);
  const canSetStatus = user?.role && ['admin', 'manager'].includes(user.role);

  // Form setup
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
    reset,
  } = useForm<ProgramFormData>({
    resolver: zodResolver(programFormSchema),
    defaultValues: {
      program_type: ProgramType.TRAINING,
      status: ProgramStatus.DRAFT,
      is_online: false,
      is_hybrid: false,
      price: 0,
      currency: 'TRY',
      min_participants: 1,
      max_participants: 50,
    },
  });

  const watchIsOnline = watch('is_online');
  const watchIsHybrid = watch('is_hybrid');

  // Load program data for edit
  useEffect(() => {
    if (isEdit && program) {
      reset({
        title: program.title,
        code: program.code,
        description: program.description || '',
        program_type: program.program_type,
        status: program.status,
        start_date: program.start_date.split('T')[0],
        end_date: program.end_date.split('T')[0],
        enrollment_start: program.enrollment_start
          ? program.enrollment_start.split('T')[0]
          : '',
        enrollment_end: program.enrollment_end
          ? program.enrollment_end.split('T')[0]
          : '',
        min_participants: program.min_participants,
        max_participants: program.max_participants,
        location: program.location || '',
        is_online: program.is_online,
        is_hybrid: program.is_hybrid,
        online_link: program.online_link || '',
        price: program.price,
        currency: program.currency,
        coordinator_id: program.coordinator_id,
      });
      setObjectives(program.objectives || []);
      setTags(program.tags || []);
    }
  }, [isEdit, program, reset]);

  // Auto-generate program code
  const handleTitleChange = (title: string) => {
    if (!isEdit && title) {
      const code = title
        .toUpperCase()
        .replace(/[^A-Z0-9\s]/g, '')
        .replace(/\s+/g, '_')
        .substring(0, 20);
      setValue('code', `PROG_${code}_${new Date().getFullYear()}`);
    }
  };

  // Add objective
  const addObjective = () => {
    if (newObjective.trim() && !objectives.includes(newObjective.trim())) {
      setObjectives([...objectives, newObjective.trim()]);
      setNewObjective('');
    }
  };

  // Remove objective
  const removeObjective = (index: number) => {
    setObjectives(objectives.filter((_, i) => i !== index));
  };

  // Add tag
  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()]);
      setNewTag('');
    }
  };

  // Remove tag
  const removeTag = (index: number) => {
    setTags(tags.filter((_, i) => i !== index));
  };

  // Form submission
  const onSubmit = async (data: ProgramFormData) => {
    try {
      const formData: CreateProgramRequest | UpdateProgramRequest = {
        ...data,
        objectives: objectives.length > 0 ? objectives : undefined,
        tags: tags.length > 0 ? tags : undefined,
        // Convert empty strings to undefined
        code: data.code || undefined,
        description: data.description || undefined,
        location: data.location || undefined,
        online_link: data.online_link || undefined,
        enrollment_start: data.enrollment_start || undefined,
        enrollment_end: data.enrollment_end || undefined,
        coordinator_id: data.coordinator_id || undefined,
      };

      if (isEdit && programId) {
        await updateProgram.mutateAsync({ id: programId, data: formData });
        toast.success(t('programs.form.messages.updateSuccess'));
        navigate('/programs');
      } else {
        await createProgram.mutateAsync(
          formData as CreateProgramRequest
        );
        toast.success(t('programs.form.messages.createSuccess'));
        navigate('/programs');
      }
    } catch (error) {
      // Error handled by mutations
    }
  };

  if (!canEdit) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">
          {t('programs.form.messages.noPermission')}
        </div>
      </Card>
    );
  }

  if (isEdit && isLoadingProgram) {
    return <FormSkeleton sections={4} fieldsPerSection={6} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/programs')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('common.backTo', { target: t('programs.title') })}
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isEdit ? t('programs.form.editProgram') : t('programs.form.newProgram')}
            </h1>
            <p className="text-gray-600">
              {isEdit
                ? t('programs.form.updateDescription')
                : t('programs.form.createDescription')}
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Information */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('programs.form.sections.basicInfo')}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">
                  {t('programs.form.fields.title')} <span className="text-destructive">*</span>
                </label>
                <Controller
                  name="title"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      error={!!errors.title}
                      onChange={(e) => {
                        field.onChange(e);
                        handleTitleChange(e.target.value);
                      }}
                    />
                  )}
                />
                {errors.title && (
                  <p className="text-sm text-destructive">
                    {errors.title.message}
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                {t('programs.form.fields.code')}
              </label>
              <Controller
                name="code"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    error={!!errors.code}
                    placeholder={t('programs.form.fields.codePlaceholder')}
                  />
                )}
              />
              {errors.code && (
                <p className="text-sm text-destructive">
                  {errors.code.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                {t('programs.form.fields.type')}
              </label>
              <Controller
                name="program_type"
                control={control}
                render={({ field }) => (
                  <Select {...field} error={!!errors.program_type}>
                    {PROGRAM_TYPE_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                )}
              />
              {errors.program_type && (
                <p className="text-sm text-destructive">
                  {errors.program_type.message}
                </p>
              )}
            </div>

            {canSetStatus && (
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">
                  {t('programs.form.fields.status')}
                </label>
                <Controller
                  name="status"
                  control={control}
                  render={({ field }) => (
                    <Select {...field} error={!!errors.status}>
                      {PROGRAM_STATUS_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </Select>
                  )}
                />
                {errors.status && (
                  <p className="text-sm text-destructive">
                    {errors.status.message}
                  </p>
                )}
              </div>
            )}

            <div className="md:col-span-2">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">
                  {t('programs.form.fields.description')}
                </label>
                <Controller
                  name="description"
                  control={control}
                  render={({ field }) => (
                    <Textarea
                      {...field}
                      error={!!errors.description}
                      rows={4}
                    />
                  )}
                />
                {errors.description && (
                  <p className="text-sm text-destructive">
                    {errors.description.message}
                  </p>
                )}
              </div>
            </div>
          </div>
        </Card>

        {/* Dates and Capacity */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('programs.form.sections.datesCapacity')}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Controller
              name="start_date"
              control={control}
              render={({ field }) => (
                <DatePicker
                  {...field}
                  label={`${t('programs.form.fields.startDate')} *`}
                  error={errors.start_date?.message || undefined}
                />
              )}
            />

            <Controller
              name="end_date"
              control={control}
              render={({ field }) => (
                <DatePicker
                  {...field}
                  label={`${t('programs.form.fields.endDate')} *`}
                  error={errors.end_date?.message || undefined}
                />
              )}
            />

            <Controller
              name="enrollment_start"
              control={control}
              render={({ field }) => (
                <DatePicker
                  {...field}
                  label={t('programs.form.fields.enrollmentStart')}
                  error={errors.enrollment_start?.message || undefined}
                />
              )}
            />

            <Controller
              name="enrollment_end"
              control={control}
              render={({ field }) => (
                <DatePicker
                  {...field}
                  label={t('programs.form.fields.enrollmentEnd')}
                  error={errors.enrollment_end?.message || undefined}
                />
              )}
            />

            <Controller
              name="min_participants"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  type="number"
                  label={t('programs.form.fields.minParticipants')}
                  error={errors.min_participants?.message}
                  onChange={(e) =>
                    field.onChange(parseInt(e.target.value) || 0)
                  }
                />
              )}
            />

            <Controller
              name="max_participants"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  type="number"
                  label={`${t('programs.form.fields.maxParticipants')} *`}
                  error={errors.max_participants?.message}
                  onChange={(e) =>
                    field.onChange(parseInt(e.target.value) || 0)
                  }
                />
              )}
            />
          </div>
        </Card>

        {/* Location and Online */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('programs.form.sections.locationFormat')}</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <Controller
                name="is_online"
                control={control}
                render={({ field }) => (
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={field.value}
                      onChange={field.onChange}
                      className="rounded border-gray-300"
                    />
                    <span>{t('programs.form.fields.onlineProgram')}</span>
                  </label>
                )}
              />

              <Controller
                name="is_hybrid"
                control={control}
                render={({ field }) => (
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={field.value}
                      onChange={field.onChange}
                      className="rounded border-gray-300"
                    />
                    <span>{t('programs.form.fields.hybridProgram')}</span>
                  </label>
                )}
              />
            </div>

            {!watchIsOnline && (
              <Controller
                name="location"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label={t('programs.form.fields.location')}
                    error={errors.location?.message}
                    placeholder={t('programs.form.fields.locationPlaceholder')}
                  />
                )}
              />
            )}

            {(watchIsOnline || watchIsHybrid) && (
              <Controller
                name="online_link"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label={t('programs.form.fields.onlineLink')}
                    error={errors.online_link?.message}
                    placeholder="https://..."
                  />
                )}
              />
            )}
          </div>
        </Card>

        {/* Price */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('programs.form.sections.pricing')}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Controller
              name="price"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  type="number"
                  step="0.01"
                  label={t('programs.form.fields.price')}
                  error={errors.price?.message}
                  onChange={(e) =>
                    field.onChange(parseFloat(e.target.value) || 0)
                  }
                />
              )}
            />

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                {t('programs.form.fields.currency')}
              </label>
              <Controller
                name="currency"
                control={control}
                render={({ field }) => (
                  <Select {...field} error={!!errors.currency}>
                    <option value="TRY">{t('currency.try')}</option>
                    <option value="USD">{t('currency.usd')}</option>
                    <option value="EUR">{t('currency.eur')}</option>
                  </Select>
                )}
              />
              {errors.currency && (
                <p className="text-sm text-destructive">
                  {errors.currency.message}
                </p>
              )}
            </div>
          </div>
        </Card>

        {/* Objectives */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('programs.form.sections.objectives')}</h3>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Input
                value={newObjective}
                onChange={(e) => setNewObjective(e.target.value)}
                placeholder={t('programs.form.fields.addObjective')}
                onKeyPress={(e) =>
                  e.key === 'Enter' && (e.preventDefault(), addObjective())
                }
              />
              <Button
                type="button"
                onClick={addObjective}
                disabled={!newObjective.trim()}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            {objectives.length > 0 && (
              <div className="space-y-2">
                {objectives.map((objective, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded"
                  >
                    <span>{objective}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeObjective(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* Tags */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('programs.form.sections.tags')}</h3>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder={t('programs.form.fields.addTag')}
                onKeyPress={(e) =>
                  e.key === 'Enter' && (e.preventDefault(), addTag())
                }
              />
              <Button type="button" onClick={addTag} disabled={!newTag.trim()}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tags.map((tag, index) => (
                  <Badge
                    key={index}
                    variant="outline"
                    className="flex items-center space-x-1"
                  >
                    <span>{tag}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeTag(index)}
                      className="p-0 h-auto"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/programs')}
          >
            {t('common.cancel')}
          </Button>
          <Button
            type="submit"
            disabled={
              isSubmitting || createProgram.isPending || updateProgram.isPending
            }
          >
            <Save className="h-4 w-4 mr-2" />
            {isEdit ? t('common.update') : t('common.create')}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ProgramForm;
