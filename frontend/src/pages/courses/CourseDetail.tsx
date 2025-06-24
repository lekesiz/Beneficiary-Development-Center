/**
 * Course Detail Page
 */
import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useCourse, useDeleteCourse, useUpdateCourseStatus } from '../../hooks/useCourses';
import { useAuth } from '../../contexts/AuthContext';
import { DataTable } from '../../components/ui/DataTable';
import { Button } from '../../components/ui/Form';
import { Badge } from '../../components/ui/Badge';
import { Card } from '../../components/ui/Card';
import { ConfirmDialog } from '../../components/ui/Modal';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { 
  getCourseStatusInfo, 
  getCourseFormatInfo, 
  getDifficultyLevelInfo,
  formatCourseDuration 
} from '../../utils/course';
import type { CourseSession } from '../../types/course';
import type { ColumnDef } from '@tanstack/react-table';
import { 
  Edit, 
  Trash2, 
  ArrowLeft, 
  Calendar, 
  Users, 
  MapPin, 
  Globe, 
  Clock, 
  User, 
  BookOpen, 
  Plus,
  Play,
  Target,
  Award,
  FileText,
  Video,
  Link as LinkIcon
} from 'lucide-react';

export const CourseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const courseId = parseInt(id!);

  const { data: course, isLoading, error } = useCourse(courseId, true);
  const deleteCourse = useDeleteCourse();
  const updateStatus = useUpdateCourseStatus();

  const [deleteConfirm, setDeleteConfirm] = useState(false);

  // Permission checks
  const canEdit = (course: any) => {
    if (user?.role === 'admin' || user?.role === 'manager') return true;
    if (user?.role === 'instructor' && course?.instructor_id === user.id) return true;
    return false;
  };
  const canDelete = user?.role === 'admin';

  // Handle delete
  const handleDelete = async () => {
    try {
      await deleteCourse.mutateAsync(courseId);
      navigate('/courses');
    } catch (error) {
      // Error handled by mutation
    }
  };

  // Handle status update
  const handleStatusUpdate = async (status: string) => {
    try {
      await updateStatus.mutateAsync({ id: courseId, status });
    } catch (error) {
      // Error handled by mutation
    }
  };

  // Session table columns
  const sessionColumns: ColumnDef<CourseSession>[] = [
    {
      accessorKey: 'title',
      header: 'Oturum Adı',
      cell: ({ row }) => (
        <div className="flex flex-col">
          <span className="font-medium">{row.original.title}</span>
          {row.original.description && (
            <span className="text-sm text-gray-500">{row.original.description}</span>
          )}
        </div>
      ),
    },
    {
      accessorKey: 'session_date',
      header: 'Tarih',
      cell: ({ row }) => (
        <div className="flex flex-col">
          <span>{new Date(row.original.session_date).toLocaleDateString('tr-TR')}</span>
          <span className="text-sm text-gray-500">
            {new Date(row.original.session_date).toLocaleTimeString('tr-TR', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </span>
        </div>
      ),
    },
    {
      accessorKey: 'duration_hours',
      header: 'Süre',
      cell: ({ row }) => `${row.original.duration_hours}sa`,
    },
    {
      accessorKey: 'location',
      header: 'Konum',
      cell: ({ row }) => (
        <div className="flex items-center space-x-2">
          {row.original.is_online ? (
            <>
              <Globe className="h-4 w-4 text-blue-500" />
              <span>Online</span>
            </>
          ) : (
            <>
              <MapPin className="h-4 w-4 text-gray-500" />
              <span>{row.original.location || '-'}</span>
            </>
          )}
        </div>
      ),
    },
    {
      accessorKey: 'instructor_name',
      header: 'Eğitmen',
      cell: ({ row }) => row.original.instructor_name || '-',
    },
    {
      accessorKey: 'is_cancelled',
      header: 'Durum',
      cell: ({ row }) => (
        <Badge color={row.original.is_cancelled ? 'red' : 'green'}>
          {row.original.is_cancelled ? 'İptal' : 'Aktif'}
        </Badge>
      ),
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !course) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">
          Kurs bulunamadı veya yüklenirken hata oluştu.
        </div>
      </Card>
    );
  }

  const statusInfo = getCourseStatusInfo(course.status);
  const formatInfo = getCourseFormatInfo(course.format);
  const difficultyInfo = getDifficultyLevelInfo(course.difficulty_level);

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
            <h1 className="text-2xl font-bold text-gray-900">{course.title}</h1>
            <div className="flex items-center space-x-2 text-gray-600">
              <span>#{course.code}</span>
              {course.program_title && (
                <>
                  <span>•</span>
                  <Link 
                    to={`/programs/${course.program_id}`}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {course.program_title}
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {canEdit(course) && (
            <Button
              variant="outline"
              onClick={() => navigate(`/courses/${course.id}/edit`)}
            >
              <Edit className="h-4 w-4 mr-2" />
              Düzenle
            </Button>
          )}
          {canDelete && (
            <Button
              variant="outline"
              onClick={() => setDeleteConfirm(true)}
              className="text-red-600 hover:text-red-800"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Sil
            </Button>
          )}
        </div>
      </div>

      {/* Status, Format, and Difficulty */}
      <div className="flex items-center space-x-4">
        <Badge color={statusInfo.color} size="lg">
          {statusInfo.label}
        </Badge>
        <div className="flex items-center space-x-2 text-gray-600">
          <span>{formatInfo.icon}</span>
          <span>{formatInfo.label}</span>
        </div>
        <Badge color={difficultyInfo.color}>
          {difficultyInfo.label}
        </Badge>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {course.participant_count || 0}
              </div>
              <div className="text-sm text-gray-600">
                {course.max_participants ? `/ ${course.max_participants}` : ''} Katılımcı
              </div>
              <div className="text-xs text-gray-500">
                {course.available_spots || 0} kişi boş
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Clock className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {course.duration_hours}
              </div>
              <div className="text-sm text-gray-600">Saat</div>
              {course.duration_weeks && (
                <div className="text-xs text-gray-500">
                  {course.duration_weeks} hafta
                </div>
              )}
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <BookOpen className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {course.session_count || 0}
              </div>
              <div className="text-sm text-gray-600">Oturum</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Target className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {Math.round(course.completion_rate || 0)}%
              </div>
              <div className="text-sm text-gray-600">Tamamlama</div>
              {course.average_score && (
                <div className="text-xs text-gray-500">
                  Ort. Puan: {Math.round(course.average_score)}
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* Course Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Kurs Bilgileri</h3>
            
            {course.subtitle && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-1">Alt Başlık</h4>
                <p className="text-gray-600">{course.subtitle}</p>
              </div>
            )}

            {course.description && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Açıklama</h4>
                <p className="text-gray-600">{course.description}</p>
              </div>
            )}

            {course.objectives && course.objectives.length > 0 && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Hedefler</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {course.objectives.map((objective, index) => (
                    <li key={index}>{objective}</li>
                  ))}
                </ul>
              </div>
            )}

            {course.prerequisites && course.prerequisites.length > 0 && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Ön Koşullar</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {course.prerequisites.map((prerequisite, index) => (
                    <li key={index}>{prerequisite}</li>
                  ))}
                </ul>
              </div>
            )}

            {course.materials && course.materials.length > 0 && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Materyaller</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {course.materials.map((material, index) => (
                    <li key={index}>{material}</li>
                  ))}
                </ul>
              </div>
            )}

            {course.tags && course.tags.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Etiketler</h4>
                <div className="flex flex-wrap gap-2">
                  {course.tags.map((tag, index) => (
                    <Badge key={index} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </div>

        {/* Side Info */}
        <div className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Detaylar</h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <BookOpen className="h-4 w-4 text-gray-400" />
                <div>
                  <div className="text-sm font-medium">Sıra</div>
                  <div className="text-sm text-gray-600">#{course.order_index}</div>
                </div>
              </div>

              {course.instructor_name && (
                <div className="flex items-center space-x-3">
                  <User className="h-4 w-4 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium">Eğitmen</div>
                    <div className="text-sm text-gray-600">
                      {course.instructor_name}
                    </div>
                  </div>
                </div>
              )}

              {course.has_assessment && (
                <div className="flex items-center space-x-3">
                  <Award className="h-4 w-4 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium">Değerlendirme</div>
                    <div className="text-sm text-gray-600">
                      {course.assessment_type || 'Var'}
                      {course.passing_score && ` (Min: ${course.passing_score})`}
                    </div>
                  </div>
                </div>
              )}

              {course.content_url && (
                <div className="flex items-center space-x-3">
                  <FileText className="h-4 w-4 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium">İçerik</div>
                    <a 
                      href={course.content_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      <LinkIcon className="h-3 w-3 inline mr-1" />
                      İçeriği Görüntüle
                    </a>
                  </div>
                </div>
              )}

              {course.video_url && (
                <div className="flex items-center space-x-3">
                  <Video className="h-4 w-4 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium">Video</div>
                    <a 
                      href={course.video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      <Play className="h-3 w-3 inline mr-1" />
                      Videoyu İzle
                    </a>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* Quick Actions */}
          {canEdit(course) && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Hızlı İşlemler</h3>
              <div className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => navigate(`/courses/${course.id}/sessions/new`)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Oturum Ekle
                </Button>
                
                {course.status === 'draft' && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => handleStatusUpdate('published')}
                    disabled={updateStatus.isPending}
                  >
                    Yayınla
                  </Button>
                )}
                
                {course.status === 'published' && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => handleStatusUpdate('archived')}
                    disabled={updateStatus.isPending}
                  >
                    Arşivle
                  </Button>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Course Sessions */}
      <Card>
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Kurs Oturumları</h3>
            {canEdit(course) && (
              <Button
                onClick={() => navigate(`/courses/${course.id}/sessions/new`)}
                size="sm"
              >
                <Plus className="h-4 w-4 mr-2" />
                Oturum Ekle
              </Button>
            )}
          </div>
        </div>
        
        <DataTable
          columns={sessionColumns}
          data={course.sessions || []}
          pagination={{
            pageIndex: 0,
            pageSize: 10,
            pageCount: 1,
            total: course.sessions?.length || 0,
          }}
          loading={false}
        />
      </Card>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={deleteConfirm}
        onClose={() => setDeleteConfirm(false)}
        onConfirm={handleDelete}
        title="Kursu Sil"
        message={`"${course.title}" kursunu silmek istediğinizden emin misiniz? Bu işlem geri alınamaz ve kursa bağlı tüm oturumlar da silinecektir.`}
        confirmText="Sil"
        cancelText="İptal"
        loading={deleteCourse.isPending}
      />
    </div>
  );
};

export default CourseDetail;