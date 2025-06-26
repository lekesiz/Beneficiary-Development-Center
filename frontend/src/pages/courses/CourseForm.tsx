/**
 * Course Form Page (Create/Edit)
 */
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft, Save, X, Plus, Info } from 'lucide-react';
import * as React from 'react';
import { useEffect, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { z } from 'zod';

import { Badge } from '../../components/ui/Badge';
import { Card } from '../../components/ui/Card';
import { DatePicker } from '../../components/ui/DatePicker';
import { FileUpload } from '../../components/ui/FileUpload';
import { Button, Input, Select, Textarea } from '../../components/ui/Form';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import {
  COURSE_STATUS_OPTIONS,
  COURSE_FORMAT_OPTIONS,
  DIFFICULTY_LEVEL_OPTIONS,
} from '../../constants/course';
import { useAuth } from '../../contexts/AuthContext';
import {
  useCourse,
  useCreateCourse,
  useUpdateCourse,
} from '../../hooks/useCourses';
import { 
  useCourseMaterialUpload, 
  useCourseMediaUpload,
  useFilesByEntity,
  useDeleteFile 
} from '../../hooks/useFiles';
import { usePrograms } from '../../hooks/usePrograms';
import {
  CourseFormat,
  CourseStatus,
  DifficultyLevel,
} from '../../types/course';
import type {
  CreateCourseRequest,
  UpdateCourseRequest,
} from '../../types/course';


// Form validation schema
const courseFormSchema = z
  .object({
    program_id: z.number().min(1, 'Program seçimi zorunludur'),
    title: z
      .string()
      .min(1, 'Kurs adı zorunludur')
      .max(200, 'Kurs adı en fazla 200 karakter olabilir'),
    subtitle: z.string().optional(),
    description: z.string().optional(),
    status: z.nativeEnum(CourseStatus).optional(),
    format: z.nativeEnum(CourseFormat).optional(),
    difficulty_level: z.nativeEnum(DifficultyLevel).optional(),
    duration_hours: z
      .number()
      .min(0.5, 'Süre en az 0.5 saat olmalıdır')
      .max(500, 'Süre en fazla 500 saat olabilir'),
    duration_weeks: z.number().min(1).max(52).optional(),
    order_index: z.number().min(1).optional(),
    objectives: z.array(z.string()).optional(),
    prerequisites: z.array(z.string()).optional(),
    materials: z.array(z.string()).optional(),
    content_url: z
      .string()
      .url('Geçerli bir URL giriniz')
      .optional()
      .or(z.literal('')),
    video_url: z
      .string()
      .url('Geçerli bir URL giriniz')
      .optional()
      .or(z.literal('')),
    has_assessment: z.boolean().optional(),
    assessment_type: z.string().optional(),
    passing_score: z.number().min(0).max(100).optional(),
    max_attempts: z.number().min(1).optional(),
    min_participants: z
      .number()
      .min(1, 'Minimum katılımcı sayısı en az 1 olmalıdır')
      .optional(),
    max_participants: z
      .number()
      .min(1, 'Maksimum katılımcı sayısı en az 1 olmalıdır')
      .optional(),
    tags: z.array(z.string()).optional(),
    thumbnail_url: z
      .string()
      .url('Geçerli bir URL giriniz')
      .optional()
      .or(z.literal('')),
    instructor_id: z.number().optional(),
  })
  .refine(
    (data) => {
      if (data.min_participants && data.max_participants) {
        return data.max_participants >= data.min_participants;
      }
      return true;
    },
    {
      message: 'Maksimum katılımcı sayısı minimum sayıdan az olamaz',
      path: ['max_participants'],
    }
  );

type CourseFormData = z.infer<typeof courseFormSchema>;

export const CourseForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const isEdit = !!id;
  const courseId = isEdit ? parseInt(id!) : null;
  const programIdFromUrl = searchParams.get('program_id')
    ? parseInt(searchParams.get('program_id')!)
    : undefined;

  // Fetch course data for edit
  const { data: course, isLoading: isLoadingCourse } = useCourse(
    courseId!,
    false
  );

  // Fetch programs for selection
  const { data: programsData } = usePrograms({ per_page: 100 });

  // Mutations
  const createCourse = useCreateCourse();
  const updateCourse = useUpdateCourse();
  const courseMaterialUpload = useCourseMaterialUpload();
  const courseMediaUpload = useCourseMediaUpload();
  const deleteFile = useDeleteFile();

  // File queries
  const { data: courseMaterials = [] } = useFilesByEntity(
    'course_material',
    courseId?.toString() || ''
  );
  const { data: courseMedia = [] } = useFilesByEntity(
    'course_media',
    courseId?.toString() || ''
  );

  // State
  const [objectives, setObjectives] = useState<string[]>([]);
  const [prerequisites, setPrerequisites] = useState<string[]>([]);
  const [materials, setMaterials] = useState<string[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [newObjective, setNewObjective] = useState('');
  const [newPrerequisite, setNewPrerequisite] = useState('');
  const [newMaterial, setNewMaterial] = useState('');
  const [newTag, setNewTag] = useState('');

  // Permission checks
  const canEdit =
    user?.role && ['admin', 'manager', 'instructor'].includes(user.role);
  const canSetStatus = user?.role && ['admin', 'manager'].includes(user.role);

  // Form setup
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
    reset,
  } = useForm<CourseFormData>({
    resolver: zodResolver(courseFormSchema),
    defaultValues: {
      program_id: programIdFromUrl,
      format: CourseFormat.LECTURE,
      status: CourseStatus.DRAFT,
      difficulty_level: DifficultyLevel.BEGINNER,
      duration_hours: 1,
      duration_weeks: 1,
      order_index: 1,
      has_assessment: false,
      min_participants: 1,
      max_participants: 20,
    },
  });

  const watchProgramId = watch('program_id');
  const watchHasAssessment = watch('has_assessment');
  const selectedProgram = programsData?.programs?.find(
    (p) => p.id === watchProgramId
  );

  // Load course data for edit
  useEffect(() => {
    if (isEdit && course) {
      reset({
        program_id: course.program_id,
        title: course.title,
        subtitle: course.subtitle || '',
        description: course.description || '',
        status: course.status,
        format: course.format,
        difficulty_level: course.difficulty_level,
        duration_hours: course.duration_hours,
        duration_weeks: course.duration_weeks || 1,
        order_index: course.order_index,
        content_url: course.content_url || '',
        video_url: course.video_url || '',
        has_assessment: course.has_assessment,
        assessment_type: course.assessment_type || '',
        passing_score: course.passing_score,
        max_attempts: course.max_attempts,
        min_participants: course.min_participants,
        max_participants: course.max_participants,
        thumbnail_url: course.thumbnail_url || '',
        instructor_id: course.instructor_id,
      });
      setObjectives(course.objectives || []);
      setPrerequisites(course.prerequisites || []);
      setMaterials(course.materials || []);
      setTags(course.tags || []);
    }
  }, [isEdit, course, reset]);

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

  // Add prerequisite
  const addPrerequisite = () => {
    if (
      newPrerequisite.trim() &&
      !prerequisites.includes(newPrerequisite.trim())
    ) {
      setPrerequisites([...prerequisites, newPrerequisite.trim()]);
      setNewPrerequisite('');
    }
  };

  // Remove prerequisite
  const removePrerequisite = (index: number) => {
    setPrerequisites(prerequisites.filter((_, i) => i !== index));
  };

  // Add material
  const addMaterial = () => {
    if (newMaterial.trim() && !materials.includes(newMaterial.trim())) {
      setMaterials([...materials, newMaterial.trim()]);
      setNewMaterial('');
    }
  };

  // Remove material
  const removeMaterial = (index: number) => {
    setMaterials(materials.filter((_, i) => i !== index));
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

  // File upload handlers
  const handleMaterialUpload = async (files: File[]) => {
    if (!courseId) return [];
    
    const results = [];
    for (const file of files) {
      try {
        const result = await courseMaterialUpload.mutateAsync({
          file,
          courseId: courseId.toString(),
        });
        results.push({
          id: result.id,
          name: result.originalName,
          size: result.size,
          type: result.mimetype,
          url: result.url,
        });
      } catch (error) {
        console.error('Failed to upload material:', error);
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

  const handleMediaUpload = async (files: File[]) => {
    if (!courseId) return [];
    
    try {
      const results = await courseMediaUpload.mutateAsync({
        files,
        courseId: courseId.toString(),
      });
      return results.map(result => ({
        id: result.id,
        name: result.originalName,
        size: result.size,
        type: result.mimetype,
        url: result.url,
      }));
    } catch (error) {
      console.error('Failed to upload media:', error);
      return files.map(file => ({
        id: `error-${Date.now()}`,
        name: file.name,
        size: file.size,
        type: file.type,
        error: 'Upload failed',
      }));
    }
  };

  const handleFileRemove = async (fileId: string) => {
    try {
      await deleteFile.mutateAsync(fileId);
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  };

  // Form submission
  const onSubmit = async (data: CourseFormData) => {
    try {
      const formData: CreateCourseRequest | UpdateCourseRequest = {
        ...data,
        objectives: objectives.length > 0 ? objectives : undefined,
        prerequisites: prerequisites.length > 0 ? prerequisites : undefined,
        materials: materials.length > 0 ? materials : undefined,
        tags: tags.length > 0 ? tags : undefined,
        // Convert empty strings to undefined
        subtitle: data.subtitle || undefined,
        description: data.description || undefined,
        content_url: data.content_url || undefined,
        video_url: data.video_url || undefined,
        thumbnail_url: data.thumbnail_url || undefined,
        assessment_type: data.assessment_type || undefined,
        instructor_id: data.instructor_id || undefined,
      };

      if (isEdit && courseId) {
        await updateCourse.mutateAsync({
          id: courseId,
          data: formData as UpdateCourseRequest,
        });
        navigate(`/courses/${courseId}`);
      } else {
        const newCourse = await createCourse.mutateAsync(
          formData as CreateCourseRequest
        );
        navigate(`/courses/${newCourse.id}`);
      }
    } catch (error) {
      // Error handled by mutations
    }
  };

  if (!canEdit) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">
          Bu sayfaya erişim yetkiniz bulunmamaktadır.
        </div>
      </Card>
    );
  }

  if (isEdit && isLoadingCourse) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/courses')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Kurslara Dön
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isEdit ? 'Kurs Düzenle' : 'Yeni Kurs'}
            </h1>
            <p className="text-gray-600">
              {isEdit
                ? 'Kurs bilgilerini güncelleyin'
                : 'Yeni bir kurs oluşturun'}
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Information */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Temel Bilgiler</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Program <span className="text-destructive">*</span>
              </label>
              <Controller
                name="program_id"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    error={!!errors.program_id}
                    onChange={(e) => field.onChange(parseInt(e.target.value))}
                    value={field.value?.toString() || ''}
                  >
                    <option value="">Program seçin</option>
                    {programsData?.programs?.map((program) => (
                      <option key={program.id} value={program.id}>
                        {program.title}
                      </option>
                    ))}
                  </Select>
                )}
              />
              {errors.program_id && (
                <p className="text-sm text-destructive">
                  {errors.program_id.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">Sıra</label>
              <Controller
                name="order_index"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    type="number"
                    error={!!errors.order_index}
                    onChange={(e) =>
                      field.onChange(parseInt(e.target.value) || 1)
                    }
                  />
                )}
              />
              {errors.order_index && (
                <p className="text-sm text-destructive">
                  {errors.order_index.message}
                </p>
              )}
            </div>

            <div className="md:col-span-2">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">
                  Kurs Adı <span className="text-destructive">*</span>
                </label>
                <Controller
                  name="title"
                  control={control}
                  render={({ field }) => (
                    <Input {...field} error={!!errors.title} />
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
                Alt Başlık
              </label>
              <Controller
                name="subtitle"
                control={control}
                render={({ field }) => (
                  <Input {...field} error={!!errors.subtitle} />
                )}
              />
              {errors.subtitle && (
                <p className="text-sm text-destructive">
                  {errors.subtitle.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">Format</label>
              <Controller
                name="format"
                control={control}
                render={({ field }) => (
                  <Select {...field} error={!!errors.format}>
                    {COURSE_FORMAT_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                )}
              />
              {errors.format && (
                <p className="text-sm text-destructive">
                  {errors.format.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Zorluk Seviyesi
              </label>
              <Controller
                name="difficulty_level"
                control={control}
                render={({ field }) => (
                  <Select {...field} error={!!errors.difficulty_level}>
                    {DIFFICULTY_LEVEL_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                )}
              />
              {errors.difficulty_level && (
                <p className="text-sm text-destructive">
                  {errors.difficulty_level.message}
                </p>
              )}
            </div>

            {canSetStatus && (
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">
                  Durum
                </label>
                <Controller
                  name="status"
                  control={control}
                  render={({ field }) => (
                    <Select {...field} error={!!errors.status}>
                      {COURSE_STATUS_OPTIONS.map((option) => (
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
                  Açıklama
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

        {/* Selected Program Info */}
        {selectedProgram && (
          <Card className="p-6 bg-blue-50 border-blue-200">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900">
                  Seçili Program: {selectedProgram.title}
                </h4>
                <p className="text-sm text-blue-700 mt-1">
                  {selectedProgram.description}
                </p>
                <div className="flex items-center space-x-4 mt-2">
                  <span className="text-xs text-blue-600">
                    Başlangıç:{' '}
                    {new Date(selectedProgram.start_date).toLocaleDateString(
                      'tr-TR'
                    )}
                  </span>
                  <span className="text-xs text-blue-600">
                    Bitiş:{' '}
                    {new Date(selectedProgram.end_date).toLocaleDateString(
                      'tr-TR'
                    )}
                  </span>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Duration and Capacity */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Süre ve Kapasite</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Süre (Saat) <span className="text-destructive">*</span>
              </label>
              <Controller
                name="duration_hours"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    type="number"
                    step="0.5"
                    error={!!errors.duration_hours}
                    onChange={(e) =>
                      field.onChange(parseFloat(e.target.value) || 0)
                    }
                  />
                )}
              />
              {errors.duration_hours && (
                <p className="text-sm text-destructive">
                  {errors.duration_hours.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Süre (Hafta)
              </label>
              <Controller
                name="duration_weeks"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    type="number"
                    error={!!errors.duration_weeks}
                    onChange={(e) =>
                      field.onChange(parseInt(e.target.value) || 1)
                    }
                  />
                )}
              />
              {errors.duration_weeks && (
                <p className="text-sm text-destructive">
                  {errors.duration_weeks.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Min. Katılımcı
              </label>
              <Controller
                name="min_participants"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    type="number"
                    error={!!errors.min_participants}
                    onChange={(e) =>
                      field.onChange(parseInt(e.target.value) || 1)
                    }
                  />
                )}
              />
              {errors.min_participants && (
                <p className="text-sm text-destructive">
                  {errors.min_participants.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Max. Katılımcı
              </label>
              <Controller
                name="max_participants"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    type="number"
                    error={!!errors.max_participants}
                    onChange={(e) =>
                      field.onChange(parseInt(e.target.value) || 1)
                    }
                  />
                )}
              />
              {errors.max_participants && (
                <p className="text-sm text-destructive">
                  {errors.max_parameters.message}
                </p>
              )}
            </div>
          </div>
        </Card>

        {/* Content and Media */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">İçerik ve Medya</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                İçerik URL
              </label>
              <Controller
                name="content_url"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    error={!!errors.content_url}
                    placeholder="https://..."
                  />
                )}
              />
              {errors.content_url && (
                <p className="text-sm text-destructive">
                  {errors.content_url.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Video URL
              </label>
              <Controller
                name="video_url"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    error={!!errors.video_url}
                    placeholder="https://..."
                  />
                )}
              />
              {errors.video_url && (
                <p className="text-sm text-destructive">
                  {errors.video_url.message}
                </p>
              )}
            </div>

            <div className="md:col-span-2">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">
                  Thumbnail URL
                </label>
                <Controller
                  name="thumbnail_url"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      error={!!errors.thumbnail_url}
                      placeholder="https://..."
                    />
                  )}
                />
                {errors.thumbnail_url && (
                  <p className="text-sm text-destructive">
                    {errors.thumbnail_url.message}
                  </p>
                )}
              </div>
            </div>
          </div>
        </Card>

        {/* File Uploads */}
        {isEdit && courseId && (
          <>
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Kurs Materyalleri</h3>
              <p className="text-sm text-gray-600 mb-4">
                PDF, DOC, PPT ve diğer belge formatlarını yükleyebilirsiniz.
              </p>
              <FileUpload
                onUpload={handleMaterialUpload}
                onRemove={handleFileRemove}
                maxFiles={10}
                maxSize={50 * 1024 * 1024} // 50MB
                acceptedTypes={[
                  'application/pdf',
                  'application/msword',
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                  'application/vnd.ms-powerpoint',
                  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                  'text/plain',
                  'application/zip',
                  'application/x-rar-compressed',
                ]}
                uploadedFiles={courseMaterials.map(file => ({
                  id: file.id,
                  name: file.name,
                  size: file.size,
                  type: file.type,
                  url: file.url,
                }))}
                className="w-full"
              />
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Medya Dosyaları</h3>
              <p className="text-sm text-gray-600 mb-4">
                Video, ses ve resim dosyalarını yükleyebilirsiniz.
              </p>
              <FileUpload
                onUpload={handleMediaUpload}
                onRemove={handleFileRemove}
                maxFiles={20}
                maxSize={200 * 1024 * 1024} // 200MB
                acceptedTypes={[
                  'image/*',
                  'video/*',
                  'audio/*',
                ]}
                uploadedFiles={courseMedia.map(file => ({
                  id: file.id,
                  name: file.name,
                  size: file.size,
                  type: file.type,
                  url: file.url,
                }))}
                className="w-full"
              />
            </Card>
          </>
        )}

        {!isEdit && (
          <Card className="p-6 bg-blue-50 border-blue-200">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900">
                  Dosya Yükleme
                </h4>
                <p className="text-sm text-blue-700 mt-1">
                  Kurs oluşturduktan sonra materyaller ve medya dosyalarını yükleyebileceksiniz.
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Assessment */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Değerlendirme</h3>
          <div className="space-y-4">
            <div>
              <Controller
                name="has_assessment"
                control={control}
                render={({ field }) => (
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={field.value}
                      onChange={field.onChange}
                      className="rounded border-gray-300"
                    />
                    <span>Bu kursun bir değerlendirmesi var</span>
                  </label>
                )}
              />
            </div>

            {watchHasAssessment && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium leading-none">
                    Değerlendirme Türü
                  </label>
                  <Controller
                    name="assessment_type"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} error={!!errors.assessment_type}>
                        <option value="">Seçiniz</option>
                        <option value="quiz">Quiz</option>
                        <option value="exam">Sınav</option>
                        <option value="project">Proje</option>
                        <option value="assignment">Ödev</option>
                      </Select>
                    )}
                  />
                  {errors.assessment_type && (
                    <p className="text-sm text-destructive">
                      {errors.assessment_type.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium leading-none">
                    Geçme Puanı (%)
                  </label>
                  <Controller
                    name="passing_score"
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        type="number"
                        min="0"
                        max="100"
                        error={!!errors.passing_score}
                        onChange={(e) =>
                          field.onChange(parseInt(e.target.value) || 0)
                        }
                      />
                    )}
                  />
                  {errors.passing_score && (
                    <p className="text-sm text-destructive">
                      {errors.passing_score.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium leading-none">
                    Max. Deneme
                  </label>
                  <Controller
                    name="max_attempts"
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        type="number"
                        min="1"
                        error={!!errors.max_attempts}
                        onChange={(e) =>
                          field.onChange(parseInt(e.target.value) || 1)
                        }
                      />
                    )}
                  />
                  {errors.max_attempts && (
                    <p className="text-sm text-destructive">
                      {errors.max_attempts.message}
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Objectives */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Kurs Hedefleri</h3>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Input
                value={newObjective}
                onChange={(e) => setNewObjective(e.target.value)}
                placeholder="Yeni hedef ekleyin"
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

        {/* Prerequisites */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Ön Koşullar</h3>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Input
                value={newPrerequisite}
                onChange={(e) => setNewPrerequisite(e.target.value)}
                placeholder="Yeni ön koşul ekleyin"
                onKeyPress={(e) =>
                  e.key === 'Enter' && (e.preventDefault(), addPrerequisite())
                }
              />
              <Button
                type="button"
                onClick={addPrerequisite}
                disabled={!newPrerequisite.trim()}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            {prerequisites.length > 0 && (
              <div className="space-y-2">
                {prerequisites.map((prerequisite, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded"
                  >
                    <span>{prerequisite}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removePrerequisite(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* Materials */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Materyaller</h3>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Input
                value={newMaterial}
                onChange={(e) => setNewMaterial(e.target.value)}
                placeholder="Yeni materyal ekleyin"
                onKeyPress={(e) =>
                  e.key === 'Enter' && (e.preventDefault(), addMaterial())
                }
              />
              <Button
                type="button"
                onClick={addMaterial}
                disabled={!newMaterial.trim()}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            {materials.length > 0 && (
              <div className="space-y-2">
                {materials.map((material, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded"
                  >
                    <span>{material}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeMaterial(index)}
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
          <h3 className="text-lg font-semibold mb-4">Etiketler</h3>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Yeni etiket ekleyin"
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
            onClick={() => navigate('/courses')}
          >
            İptal
          </Button>
          <Button
            type="submit"
            disabled={
              isSubmitting || createCourse.isPending || updateCourse.isPending
            }
          >
            <Save className="h-4 w-4 mr-2" />
            {isEdit ? 'Güncelle' : 'Oluştur'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CourseForm;
