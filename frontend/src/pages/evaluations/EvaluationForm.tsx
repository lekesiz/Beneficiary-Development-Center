import { zodResolver } from '@hookform/resolvers/zod';
import {
  ArrowLeft,
  Save,
  Clock,
  Users,
  FileText,
  Settings,
  Calendar,
  Info,
  Brain,
} from 'lucide-react';
import * as React from 'react';
import { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';
import { z } from 'zod';

import { Card } from '@/components/ui/Card';
import { DatePicker } from '@/components/ui/DatePicker';
import { FormField, Input, Textarea, Select, Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { TagInput } from '@/components/ui/TagInput';
import { useCourses } from '@/hooks/useCourses';
import { useEvaluation, useCreateEvaluation, useUpdateEvaluation } from '@/hooks/useEvaluations';
import { usePrograms } from '@/hooks/usePrograms';
import type { CreateEvaluationRequest, UpdateEvaluationRequest } from '@/types/evaluation';

// Zod validation schema
const evaluationSchema = z
  .object({
    title: z.string().min(1, 'Title is required').max(200, 'Title can be at most 200 characters'),
    description: z.string().optional(),
    instructions: z.string().optional(),
    course_id: z.number().optional(),
    program_id: z.number().optional(),
    time_limit_minutes: z
      .number()
      .min(1, 'Duration must be at least 1 minute')
      .max(1440, 'Duration can be at most 24 hours')
      .optional(),
    max_attempts: z
      .number()
      .min(1, 'Maximum attempts must be at least 1')
      .max(10, 'Maximum attempts can be at most 10')
      .default(1),
    passing_score: z
      .number()
      .min(0, 'Passing score must be between 0-100')
      .max(100, 'Passing score must be between 0-100')
      .default(70),
    shuffle_questions: z.boolean().default(false),
    show_results_immediately: z.boolean().default(true),
    allow_review: z.boolean().default(true),
    is_adaptive: z.boolean().default(false),
    available_from: z.string().optional(),
    available_until: z.string().optional(),
    tags: z.array(z.string()).default([]),
  })
  .refine(
    (data) => {
      // At least one of course_id or program_id must be selected
      return data.course_id || data.program_id;
    },
    {
      message: 'Course or program must be selected',
      path: ['course_id'],
    }
  )
  .refine(
    (data) => {
      // If both dates are provided, available_from must be before available_until
      if (data.available_from && data.available_until) {
        return new Date(data.available_from) < new Date(data.available_until);
      }
      return true;
    },
    {
      message: 'Start date must be before end date',
      path: ['available_until'],
    }
  );

type EvaluationFormData = z.infer<typeof evaluationSchema>;

interface EvaluationFormProps {
  mode: 'create' | 'edit';
}

const EvaluationForm: React.FC<EvaluationFormProps> = ({ mode }) => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const evaluationId = id ? parseInt(id) : undefined;

  // React Query hooks
  const { data: evaluation, isLoading: evaluationLoading } = useEvaluation(evaluationId!, false, {
    enabled: mode === 'edit' && !!evaluationId,
  });
  const { data: coursesData } = useCourses({ per_page: 100 });
  const { data: programsData } = usePrograms({ per_page: 100 });
  const createMutation = useCreateEvaluation();
  const updateMutation = useUpdateEvaluation();

  // Form setup
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
    setValue,
  } = useForm<EvaluationFormData>({
    resolver: zodResolver(evaluationSchema),
    defaultValues: {
      title: '',
      description: '',
      instructions: '',
      max_attempts: 1,
      passing_score: 70,
      shuffle_questions: false,
      show_results_immediately: true,
      allow_review: true,
      is_adaptive: false,
      tags: [],
    },
  });

  // Watch form values for dynamic behavior
  const watchedProgramId = watch('program_id');

  // Reset form when evaluation data is loaded
  useEffect(() => {
    if (mode === 'edit' && evaluation) {
      reset({
        title: evaluation.title,
        description: evaluation.description || '',
        instructions: evaluation.instructions || '',
        course_id: evaluation.course_id || undefined,
        program_id: evaluation.program_id || undefined,
        time_limit_minutes: evaluation.time_limit_minutes || undefined,
        max_attempts: evaluation.max_attempts,
        passing_score: evaluation.passing_score,
        shuffle_questions: evaluation.shuffle_questions,
        show_results_immediately: evaluation.show_results_immediately,
        allow_review: evaluation.allow_review,
        is_adaptive: evaluation.is_adaptive || false,
        available_from: evaluation.available_from || undefined,
        available_until: evaluation.available_until || undefined,
        tags: evaluation.tags || [],
      });
    }
  }, [mode, evaluation, reset]);

  // Filter courses by selected program
  const filteredCourses = React.useMemo(() => {
    if (!coursesData?.courses) return [];
    if (!watchedProgramId) return coursesData.courses;
    return coursesData.courses.filter((course) => course.program_id === watchedProgramId);
  }, [coursesData?.courses, watchedProgramId]);

  // Handle form submission
  const onSubmit = async (data: EvaluationFormData) => {
    try {
      // Convert string dates to ISO format
      const formattedData = {
        ...data,
        available_from: data.available_from
          ? new Date(data.available_from).toISOString()
          : undefined,
        available_until: data.available_until
          ? new Date(data.available_until).toISOString()
          : undefined,
      };

      if (mode === 'create') {
        const newEvaluation = await createMutation.mutateAsync(
          formattedData as CreateEvaluationRequest
        );
        navigate(`/evaluations/${newEvaluation.id}`);
      } else if (mode === 'edit' && evaluationId) {
        const updatedEvaluation = await updateMutation.mutateAsync({
          id: evaluationId,
          data: formattedData as UpdateEvaluationRequest,
        });
        navigate(`/evaluations/${updatedEvaluation.id}`);
      }
    } catch (error) {
      // Error handling is done by the mutation hooks with toast
      console.error('Form submission error:', error);
    }
  };

  if (mode === 'edit' && evaluationLoading) {
    return (
      <div className="p-6 flex justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={() => navigate('/evaluations')}
          className="p-2 hover:bg-gray-100 rounded-md"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold">
            {mode === 'create' ? 'New Evaluation' : 'Edit Evaluation'}
          </h1>
          <p className="text-gray-600">
            {mode === 'create' ? 'Create a new evaluation' : 'Edit existing evaluation'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Information */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Info className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold">Basic Information</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <Controller
                name="title"
                control={control}
                render={({ field }) => (
                  <FormField label="Title" error={errors.title?.message} required>
                    <Input {...field} placeholder="Enter evaluation title" error={!!errors.title} />
                  </FormField>
                )}
              />
            </div>

            <div className="md:col-span-2">
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <FormField label="Description" error={errors.description?.message}>
                    <Textarea
                      {...field}
                      placeholder="Brief description about the evaluation"
                      rows={3}
                      error={!!errors.description}
                    />
                  </FormField>
                )}
              />
            </div>

            <div className="md:col-span-2">
              <Controller
                name="instructions"
                control={control}
                render={({ field }) => (
                  <FormField label="Instructions" error={errors.instructions?.message}>
                    <Textarea
                      {...field}
                      placeholder="Evaluation instructions for students"
                      rows={4}
                      error={!!errors.instructions}
                    />
                  </FormField>
                )}
              />
            </div>
          </div>
        </Card>

        {/* Program and Course Selection */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <FileText className="h-5 w-5 text-green-600" />
            <h2 className="text-lg font-semibold">Program and Course</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Controller
              name="program_id"
              control={control}
              render={({ field }) => (
                <FormField label="Program" error={errors.program_id?.message}>
                  <Select
                    {...field}
                    value={field.value || ''}
                    onChange={(e) => {
                      const value = e.target.value ? parseInt(e.target.value) : undefined;
                      field.onChange(value);
                      // Clear course selection when program changes
                      setValue('course_id', undefined);
                    }}
                    error={!!errors.program_id}
                  >
                    <option value="">Select program</option>
                    {programsData?.programs.map((program) => (
                      <option key={program.id} value={program.id}>
                        {program.title}
                      </option>
                    ))}
                  </Select>
                </FormField>
              )}
            />

            <Controller
              name="course_id"
              control={control}
              render={({ field }) => (
                <FormField label="Course" error={errors.course_id?.message}>
                  <Select
                    {...field}
                    value={field.value || ''}
                    onChange={(e) => {
                      const value = e.target.value ? parseInt(e.target.value) : undefined;
                      field.onChange(value);
                    }}
                    error={!!errors.course_id}
                    disabled={!watchedProgramId}
                  >
                    <option value="">Select course</option>
                    {filteredCourses.map((course) => (
                      <option key={course.id} value={course.id}>
                        {course.title}
                      </option>
                    ))}
                  </Select>
                </FormField>
              )}
            />
          </div>

          {!watchedProgramId && (
            <p className="text-sm text-gray-500 mt-2">Select a program first to choose a course</p>
          )}
        </Card>

        {/* Settings */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Settings className="h-5 w-5 text-purple-600" />
            <h2 className="text-lg font-semibold">Settings</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Controller
              name="time_limit_minutes"
              control={control}
              render={({ field }) => (
                <FormField label="Time Limit (minutes)" error={errors.time_limit_minutes?.message}>
                  <Input
                    {...field}
                    type="number"
                    min="1"
                    max="1440"
                    placeholder="e.g.: 60"
                    onChange={(e) =>
                      field.onChange(e.target.value ? parseInt(e.target.value) : undefined)
                    }
                    error={!!errors.time_limit_minutes}
                  />
                </FormField>
              )}
            />

            <Controller
              name="max_attempts"
              control={control}
              render={({ field }) => (
                <FormField label="Maximum Attempts" error={errors.max_attempts?.message} required>
                  <Input
                    {...field}
                    type="number"
                    min="1"
                    max="10"
                    onChange={(e) => field.onChange(parseInt(e.target.value))}
                    error={!!errors.max_attempts}
                  />
                </FormField>
              )}
            />

            <Controller
              name="passing_score"
              control={control}
              render={({ field }) => (
                <FormField label="Passing Score (%)" error={errors.passing_score?.message} required>
                  <Input
                    {...field}
                    type="number"
                    min="0"
                    max="100"
                    onChange={(e) => field.onChange(parseFloat(e.target.value))}
                    error={!!errors.passing_score}
                  />
                </FormField>
              )}
            />
          </div>

          {/* Boolean Settings */}
          <div className="mt-6 space-y-4">
            <Controller
              name="shuffle_questions"
              control={control}
              render={({ field }) => (
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={field.value}
                    onChange={field.onChange}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm font-medium">Shuffle questions</span>
                </label>
              )}
            />

            <Controller
              name="show_results_immediately"
              control={control}
              render={({ field }) => (
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={field.value}
                    onChange={field.onChange}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm font-medium">Show results immediately</span>
                </label>
              )}
            />

            <Controller
              name="allow_review"
              control={control}
              render={({ field }) => (
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={field.value}
                    onChange={field.onChange}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm font-medium">Allow review</span>
                </label>
              )}
            />

            <Controller
              name="is_adaptive"
              control={control}
              render={({ field }) => (
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={field.value}
                    onChange={field.onChange}
                    className="rounded border-gray-300"
                  />
                  <div className="flex items-center space-x-2">
                    <Brain className="h-4 w-4 text-purple-600" />
                    <span className="text-sm font-medium">AI Powered Adaptive Evaluation</span>
                  </div>
                </label>
              )}
            />

            {watch('is_adaptive') && (
              <div className="mt-2 p-3 bg-purple-50 rounded-lg">
                <p className="text-sm text-purple-700">
                  <strong>Adaptive mode enabled:</strong> Questions will be automatically adjusted
                  by AI based on student performance. Difficulty level will change dynamically.
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Availability */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Calendar className="h-5 w-5 text-orange-600" />
            <h2 className="text-lg font-semibold">Availability</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Controller
              name="available_from"
              control={control}
              render={({ field }) => (
                <FormField label="Start Date" error={errors.available_from?.message}>
                  <Input {...field} type="datetime-local" error={!!errors.available_from} />
                </FormField>
              )}
            />

            <Controller
              name="available_until"
              control={control}
              render={({ field }) => (
                <FormField label="End Date" error={errors.available_until?.message}>
                  <Input {...field} type="datetime-local" error={!!errors.available_until} />
                </FormField>
              )}
            />
          </div>
        </Card>

        {/* Tags */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <span className="text-lg">#</span>
            <h2 className="text-lg font-semibold">Tags</h2>
          </div>

          <Controller
            name="tags"
            control={control}
            render={({ field }) => (
              <FormField label="Tags" error={errors.tags?.message}>
                <TagInput
                  value={field.value}
                  onChange={field.onChange}
                  placeholder="Type and press Enter to add tags"
                />
              </FormField>
            )}
          />
        </Card>

        {/* Form Actions */}
        <div className="flex justify-end space-x-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/evaluations')}
            disabled={isSubmitting}
          >
            Cancel
          </Button>

          <Button type="submit" loading={isSubmitting} disabled={isSubmitting}>
            <Save className="mr-2 h-4 w-4" />
            {mode === 'create' ? 'Create' : 'Update'}
          </Button>
        </div>
      </form>
    </div>
  );
};

// Create and Edit page components
export const CreateEvaluationPage = () => <EvaluationForm mode="create" />;
export const EditEvaluationPage = () => <EvaluationForm mode="edit" />;

export default EvaluationForm;
