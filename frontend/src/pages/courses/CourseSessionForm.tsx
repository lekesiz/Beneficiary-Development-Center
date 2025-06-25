/**
 * Course Session Form Page (Create/Edit)
 */
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft, Save, Calendar, MapPin, Globe } from 'lucide-react';
import * as React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useParams, useNavigate } from 'react-router-dom';
import { z } from 'zod';

import { Card } from '../../components/ui/Card';
import { DatePicker } from '../../components/ui/DatePicker';
import { Button, Input, Select, Textarea } from '../../components/ui/Form';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import { useCourse, useAddSession } from '../../hooks/useCourses';
import type { CreateSessionRequest } from '../../types/course';


// Form validation schema
const sessionFormSchema = z.object({
  title: z
    .string()
    .min(1, 'Oturum adı zorunludur')
    .max(200, 'Oturum adı en fazla 200 karakter olabilir'),
  description: z.string().optional(),
  session_date: z.string().min(1, 'Tarih zorunludur'),
  session_time: z.string().min(1, 'Saat zorunludur'),
  duration_hours: z
    .number()
    .min(0.5, 'Süre en az 0.5 saat olmalıdır')
    .max(12, 'Süre en fazla 12 saat olabilir'),
  location: z.string().optional(),
  room_number: z.string().optional(),
  is_online: z.boolean(),
  online_link: z
    .string()
    .url('Geçerli bir URL giriniz')
    .optional()
    .or(z.literal('')),
  instructor_id: z.number().optional(),
  is_mandatory: z.boolean(),
  materials_url: z
    .string()
    .url('Geçerli bir URL giriniz')
    .optional()
    .or(z.literal('')),
});

type SessionFormData = z.infer<typeof sessionFormSchema>;

export const CourseSessionForm: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const courseIdNum = parseInt(courseId!);

  const { data: course, isLoading: isLoadingCourse } = useCourse(
    courseIdNum,
    false
  );
  const addSession = useAddSession();

  // Permission checks
  const canEdit = (course: any) => {
    if (user?.role === 'admin' || user?.role === 'manager') return true;
    if (user?.role === 'instructor' && course?.instructor_id === user.id)
      return true;
    return false;
  };

  // Form setup
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<SessionFormData>({
    resolver: zodResolver(sessionFormSchema),
    defaultValues: {
      duration_hours: 2,
      is_online: false,
      is_mandatory: true,
    },
  });

  const watchIsOnline = watch('is_online');

  // Form submission
  const onSubmit = async (data: SessionFormData) => {
    try {
      const sessionDateTime = new Date(
        `${data.session_date}T${data.session_time}`
      );

      const sessionData: CreateSessionRequest = {
        title: data.title,
        description: data.description || undefined,
        session_date: sessionDateTime.toISOString(),
        duration_hours: data.duration_hours,
        location: data.location || undefined,
        room_number: data.room_number || undefined,
        is_online: data.is_online,
        online_link: data.online_link || undefined,
        instructor_id: data.instructor_id || undefined,
        is_mandatory: data.is_mandatory,
        materials_url: data.materials_url || undefined,
      };

      await addSession.mutateAsync({ courseId: courseIdNum, sessionData });
      navigate(`/courses/${courseId}`);
    } catch (error) {
      // Error handled by mutation
    }
  };

  if (isLoadingCourse) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!course || !canEdit(course)) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">
          Bu sayfaya erişim yetkiniz bulunmamaktadır veya kurs bulunamadı.
        </div>
      </Card>
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
            onClick={() => navigate(`/courses/${courseId}`)}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Kursa Dön
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Yeni Oturum</h1>
            <p className="text-gray-600">
              {course.title} için yeni oturum oluşturun
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Information */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Oturum Bilgileri</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">
                  Oturum Adı <span className="text-destructive">*</span>
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
                      rows={3}
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

        {/* Date and Time */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Tarih ve Süre</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Controller
              name="session_date"
              control={control}
              render={({ field }) => (
                <DatePicker
                  {...field}
                  label="Tarih *"
                  error={errors.session_date?.message}
                />
              )}
            />

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Saat <span className="text-destructive">*</span>
              </label>
              <Controller
                name="session_time"
                control={control}
                render={({ field }) => (
                  <Input {...field} type="time" error={!!errors.session_time} />
                )}
              />
              {errors.session_time && (
                <p className="text-sm text-destructive">
                  {errors.session_time.message}
                </p>
              )}
            </div>

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
                    min="0.5"
                    max="12"
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
          </div>
        </Card>

        {/* Location */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Konum ve Format</h3>
          <div className="space-y-4">
            <div>
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
                    <span>Online Oturum</span>
                  </label>
                )}
              />
            </div>

            {!watchIsOnline && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium leading-none">
                    Konum
                  </label>
                  <Controller
                    name="location"
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        error={!!errors.location}
                        placeholder="Oturum konumu"
                      />
                    )}
                  />
                  {errors.location && (
                    <p className="text-sm text-destructive">
                      {errors.location.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium leading-none">
                    Oda Numarası
                  </label>
                  <Controller
                    name="room_number"
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        error={!!errors.room_number}
                        placeholder="Oda/salon numarası"
                      />
                    )}
                  />
                  {errors.room_number && (
                    <p className="text-sm text-destructive">
                      {errors.room_number.message}
                    </p>
                  )}
                </div>
              </div>
            )}

            {watchIsOnline && (
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">
                  Online Link
                </label>
                <Controller
                  name="online_link"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      error={!!errors.online_link}
                      placeholder="https://..."
                    />
                  )}
                />
                {errors.online_link && (
                  <p className="text-sm text-destructive">
                    {errors.online_link.message}
                  </p>
                )}
              </div>
            )}
          </div>
        </Card>

        {/* Additional Settings */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Ek Ayarlar</h3>
          <div className="space-y-4">
            <div>
              <Controller
                name="is_mandatory"
                control={control}
                render={({ field }) => (
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={field.value}
                      onChange={field.onChange}
                      className="rounded border-gray-300"
                    />
                    <span>Zorunlu Oturum</span>
                  </label>
                )}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Materyal URL
              </label>
              <Controller
                name="materials_url"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    error={!!errors.materials_url}
                    placeholder="https://..."
                  />
                )}
              />
              {errors.materials_url && (
                <p className="text-sm text-destructive">
                  {errors.materials_url.message}
                </p>
              )}
            </div>
          </div>
        </Card>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate(`/courses/${courseId}`)}
          >
            İptal
          </Button>
          <Button type="submit" disabled={isSubmitting || addSession.isPending}>
            <Save className="h-4 w-4 mr-2" />
            Oturum Oluştur
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CourseSessionForm;
