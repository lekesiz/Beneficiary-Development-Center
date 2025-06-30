/**
 * Program Detail Page
 */
import type { ColumnDef } from '@tanstack/react-table';
import {
  Edit,
  Trash2,
  ArrowLeft,
  Calendar,
  Users,
  MapPin,
  Globe,
  DollarSign,
  User,
  BookOpen,
  Plus,
  Eye,
  Clock,
  Target,
  ArrowUpDown,
} from 'lucide-react';
import * as React from 'react';
import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';

import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { DataTable } from '../../components/ui/DataTable';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { useAuth } from '../../hooks/useAuth';
import { useCourses } from '../../hooks/useCourses';
import { useProgram, useDeleteProgram, useUpdateProgramStatus } from '../../hooks/usePrograms';
import type { Course } from '../../types/course';
import {
  getCourseStatusInfo,
  getCourseFormatInfo,
  getDifficultyLevelInfo,
} from '../../utils/course';
import {
  formatProgramDate,
  getProgramStatusInfo,
  getProgramTypeInfo,
  formatProgramPrice,
} from '../../utils/program';

export const ProgramDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const programId = parseInt(id!);

  const { data: program, isLoading, error } = useProgram(programId, true);
  const { data: coursesData } = useCourses({
    program_id: programId,
    per_page: 100,
  });
  const deleteProgram = useDeleteProgram();
  const updateStatus = useUpdateProgramStatus();

  const [deleteConfirm, setDeleteConfirm] = useState(false);

  // Permission checks
  const canEdit = user?.roles?.some(role => ['admin', 'manager', 'trainer'].includes(role.name)) || 
                  user?.primaryRole && ['admin', 'manager', 'trainer'].includes(user.primaryRole);
  const canDelete = user?.roles?.some(role => ['admin'].includes(role.name)) || 
                    user?.primaryRole === 'admin';

  // Handle delete
  const handleDelete = async () => {
    try {
      await deleteProgram.mutateAsync(programId);
      navigate('/programs');
    } catch (error) {
      // Error handled by mutation
    }
  };

  // Handle status update
  const handleStatusUpdate = async (status: string) => {
    try {
      await updateStatus.mutateAsync({ id: programId, status });
    } catch (error) {
      // Error handled by mutation
    }
  };

  // Course table columns
  const courseColumns: ColumnDef<Course>[] = [
    {
      accessorKey: 'title',
      header: 'Kurs Adı',
      cell: ({ row }) => (
        <div className="flex flex-col">
          <Link
            to={`/courses/${row.original.id}`}
            className="font-medium text-blue-600 hover:text-blue-800"
          >
            {row.original.title}
          </Link>
          <span className="text-sm text-gray-500">#{row.original.order_index}</span>
        </div>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Durum',
      cell: ({ row }) => {
        const statusInfo = getCourseStatusInfo(row.original.status);
        return <Badge color={statusInfo.color}>{statusInfo.label}</Badge>;
      },
    },
    {
      accessorKey: 'format',
      header: 'Format',
      cell: ({ row }) => {
        const formatInfo = getCourseFormatInfo(row.original.format);
        return (
          <div className="flex items-center space-x-2">
            <span>{formatInfo.icon}</span>
            <span>{formatInfo.label}</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'difficulty_level',
      header: 'Zorluk',
      cell: ({ row }) => {
        const difficultyInfo = getDifficultyLevelInfo(row.original.difficulty_level);
        return <Badge color={difficultyInfo.color}>{difficultyInfo.label}</Badge>;
      },
    },
    {
      accessorKey: 'duration_hours',
      header: 'Süre',
      cell: ({ row }) => `${row.original.duration_hours || 0}sa`,
    },
    {
      accessorKey: 'instructor_name',
      header: 'Eğitmen',
      cell: ({ row }) => row.original.instructor_name || '-',
    },
    {
      id: 'actions',
      header: 'İşlemler',
      cell: ({ row }) => (
        <Button variant="ghost" size="sm" onClick={() => navigate(`/courses/${row.original.id}`)}>
          <Eye className="h-4 w-4" />
        </Button>
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

  if (error || !program) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">
          Program bulunamadı veya yüklenirken hata oluştu.
        </div>
      </Card>
    );
  }

  const statusInfo = getProgramStatusInfo(program.status);
  const typeInfo = getProgramTypeInfo(program.program_type);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/programs')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Programlara Dön
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{program.title}</h1>
            <p className="text-gray-600">#{program.code}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {canEdit && (
            <Button variant="outline" onClick={() => navigate(`/programs/${program.id}/edit`)}>
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

      {/* Status and Type */}
      <div className="flex items-center space-x-4">
        <Badge color={statusInfo.color} size="lg">
          {statusInfo.label}
        </Badge>
        <div className="flex items-center space-x-2 text-gray-600">
          <span>{typeInfo.icon}</span>
          <span>{typeInfo.label}</span>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{program.enrollment_count || 0}</div>
              <div className="text-sm text-gray-600">/ {program.max_participants} Katılımcı</div>
              <div className="text-xs text-gray-500">{program.available_spots || 0} kişi boş</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <BookOpen className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{program.course_count || 0}</div>
              <div className="text-sm text-gray-600">Kurs</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Clock className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{program.duration_days}</div>
              <div className="text-sm text-gray-600">Gün</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Target className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{Math.round(program.completion_rate || 0)}%</div>
              <div className="text-sm text-gray-600">Tamamlama</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Program Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Program Bilgileri</h3>

            {program.description && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Açıklama</h4>
                <p className="text-gray-600">{program.description}</p>
              </div>
            )}

            {program.objectives && program.objectives.length > 0 && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Hedefler</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {program.objectives.map((objective, index) => (
                    <li key={index}>{objective}</li>
                  ))}
                </ul>
              </div>
            )}

            {program.tags && program.tags.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Etiketler</h4>
                <div className="flex flex-wrap gap-2">
                  {program.tags.map((tag, index) => (
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
                <Calendar className="h-4 w-4 text-gray-400" />
                <div>
                  <div className="text-sm font-medium">Başlangıç</div>
                  <div className="text-sm text-gray-600">
                    {formatProgramDate(program.start_date, 'dd MMMM yyyy')}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Calendar className="h-4 w-4 text-gray-400" />
                <div>
                  <div className="text-sm font-medium">Bitiş</div>
                  <div className="text-sm text-gray-600">
                    {formatProgramDate(program.end_date, 'dd MMMM yyyy')}
                  </div>
                </div>
              </div>

              {program.location && (
                <div className="flex items-center space-x-3">
                  <MapPin className="h-4 w-4 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium">Konum</div>
                    <div className="text-sm text-gray-600">{program.location}</div>
                  </div>
                </div>
              )}

              {program.is_online && (
                <div className="flex items-center space-x-3">
                  <Globe className="h-4 w-4 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium">Online</div>
                    <div className="text-sm text-gray-600">
                      {program.is_hybrid ? 'Hibrit' : 'Tam Online'}
                    </div>
                  </div>
                </div>
              )}

              <div className="flex items-center space-x-3">
                <DollarSign className="h-4 w-4 text-gray-400" />
                <div>
                  <div className="text-sm font-medium">Ücret</div>
                  <div className="text-sm text-gray-600">
                    {formatProgramPrice(program.price, program.currency)}
                  </div>
                </div>
              </div>

              {program.coordinator_name && (
                <div className="flex items-center space-x-3">
                  <User className="h-4 w-4 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium">Koordinatör</div>
                    <div className="text-sm text-gray-600">{program.coordinator_name}</div>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* Quick Actions */}
          {canEdit && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Hızlı İşlemler</h3>
              <div className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => navigate(`/courses/new?program_id=${program.id}`)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Kurs Ekle
                </Button>

                {program.course_count && program.course_count > 1 && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => navigate(`/programs/${program.id}/courses/reorder`)}
                  >
                    <ArrowUpDown className="h-4 w-4 mr-2" />
                    Kurs Sıralaması
                  </Button>
                )}

                {program.status === 'draft' && (
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

                {program.status === 'published' && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => handleStatusUpdate('active')}
                    disabled={updateStatus.isPending}
                  >
                    Aktif Et
                  </Button>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Courses Table */}
      <Card>
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Program Kursları</h3>
            {canEdit && (
              <Button onClick={() => navigate(`/courses/new?program_id=${program.id}`)} size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Kurs Ekle
              </Button>
            )}
          </div>
        </div>

        <DataTable
          columns={courseColumns}
          data={coursesData?.courses || []}
          pagination={{
            pageIndex: 0,
            pageSize: 10,
            pageCount: 1,
            total: coursesData?.courses?.length || 0,
          }}
          loading={false}
        />
      </Card>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={deleteConfirm}
        onClose={() => setDeleteConfirm(false)}
        onConfirm={handleDelete}
        title="Programı Sil"
        description={`"${program.title}" programını silmek istediğinizden emin misiniz? Bu işlem geri alınamaz ve programa bağlı tüm kurslar da silinecektir.`}
        confirmText="Sil"
        cancelText="İptal"
        loading={deleteProgram.isPending}
      />
    </div>
  );
};

export default ProgramDetail;
