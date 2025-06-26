/**
 * Course List Page
 */
import type { ColumnDef, SortingState } from '@tanstack/react-table';
import {
  Edit,
  Eye,
  Trash2,
  Plus,
  Search,
  Filter,
  Copy,
  ArrowUpDown,
  GraduationCap,
} from 'lucide-react';
import * as React from 'react';
import { useState, useMemo } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { DataTableSkeleton } from '../../components/common/DataTableSkeleton';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { DataTable } from '../../components/ui/DataTable';
import { EmptyState } from '../../components/ui/EmptyState';
import { Input } from '../../components/ui/Input';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { Select } from '../../components/ui/Select';
import {
  COURSE_STATUS_OPTIONS,
  COURSE_FORMAT_OPTIONS,
  DIFFICULTY_LEVEL_OPTIONS,
} from '../../constants/course';
import { useAuth } from '../../hooks/useAuth';
import { useCourses, useDeleteCourse } from '../../hooks/useCourses';
import { usePrograms } from '../../hooks/usePrograms';
import type { Course, CourseFilters } from '../../types/course';
import {
  getCourseStatusInfo,
  getCourseFormatInfo,
  getDifficultyLevelInfo,
  formatCourseDuration,
} from '../../utils/course';

export const CourseList: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user } = useAuth();
  const { t } = useTranslation();
  const deleteCourse = useDeleteCourse();

  // Initialize filters from URL params
  const [filters, setFilters] = useState<CourseFilters>({
    page: 1,
    per_page: 20,
    program_id: searchParams.get('program_id')
      ? parseInt(searchParams.get('program_id')!)
      : undefined,
  });
  const [search, setSearch] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    course?: Course;
  }>({
    isOpen: false,
  });

  // Update filters when sorting changes
  React.useEffect(() => {
    if (sorting.length > 0) {
      const sort = sorting[0];
      setFilters((prev) => ({
        ...prev,
        sort_by: sort.id,
        sort_order: sort.desc ? 'desc' : 'asc',
        page: 1, // Reset to first page on sort change
      }));
    } else {
      setFilters((prev) => ({
        ...prev,
        sort_by: undefined,
        sort_order: undefined,
      }));
    }
  }, [sorting]);

  // Fetch courses and programs
  const { data, isLoading, error } = useCourses(filters);
  const { data: programsData } = usePrograms({ per_page: 100 }); // For filter dropdown

  // Permission checks
  const canCreate =
    user?.role && ['admin', 'manager', 'instructor'].includes(user.role);
  const canEdit = (course: Course) => {
    if (user?.role === 'admin' || user?.role === 'manager') return true;
    if (user?.role === 'instructor' && course.instructor_id === user.id)
      return true;
    return false;
  };
  const canDelete = user?.role === 'admin';

  // Handle search
  const handleSearch = (value: string) => {
    setSearch(value);
    setFilters((prev) => ({
      ...prev,
      search: value || undefined,
      page: 1,
    }));
  };

  // Handle filter changes
  const handleFilterChange = (key: keyof CourseFilters, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
      page: 1,
    }));
  };

  // Handle pagination
  const handlePageChange = (page: number) => {
    setFilters((prev) => ({ ...prev, page }));
  };

  // Handle delete
  const handleDelete = async (course: Course) => {
    try {
      await deleteCourse.mutateAsync(course.id);
      setDeleteConfirm({ isOpen: false });
    } catch (error) {
      // Error handled by mutation
    }
  };

  // Handle duplicate
  const handleDuplicate = (course: Course) => {
    // Navigate to duplicate form or handle directly
    navigate(`/courses/${course.id}/duplicate`);
  };

  // Table columns
  const columns = useMemo<ColumnDef<Course>[]>(
    () => [
      {
        accessorKey: 'title',
        header: t('courses.list.columns.name'),
        enableSorting: true,
        cell: ({ row }) => (
          <div className="flex flex-col">
            <Link
              to={`/courses/${row.original.id}`}
              className="font-medium text-blue-600 hover:text-blue-800"
            >
              {row.original.title}
            </Link>
            <span className="text-sm text-gray-500">{row.original.code}</span>
            {row.original.subtitle && (
              <span className="text-xs text-gray-400">
                {row.original.subtitle}
              </span>
            )}
          </div>
        ),
      },
      {
        accessorKey: 'program_title',
        header: t('courses.list.columns.program'),
        cell: ({ row }) => (
          <div className="flex flex-col">
            <span className="text-sm font-medium">
              {row.original.program_title}
            </span>
            <span className="text-xs text-gray-500">
              #{row.original.order_index}
            </span>
          </div>
        ),
      },
      {
        accessorKey: 'status',
        header: t('courses.list.columns.status'),
        enableSorting: true,
        cell: ({ row }) => {
          const statusInfo = getCourseStatusInfo(row.original.status);
          return <Badge color={statusInfo.color}>{statusInfo.label}</Badge>;
        },
      },
      {
        accessorKey: 'format',
        header: t('courses.list.columns.format'),
        enableSorting: true,
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
        header: t('courses.list.columns.difficulty'),
        enableSorting: true,
        cell: ({ row }) => {
          const difficultyInfo = getDifficultyLevelInfo(
            row.original.difficulty_level
          );
          return (
            <Badge color={difficultyInfo.color}>{difficultyInfo.label}</Badge>
          );
        },
      },
      {
        accessorKey: 'duration_hours',
        header: t('courses.list.columns.duration'),
        enableSorting: true,
        cell: ({ row }) =>
          formatCourseDuration(
            row.original.total_duration_hours || row.original.duration_hours
          ),
      },
      {
        accessorKey: 'participant_count',
        header: t('courses.list.columns.participants'),
        cell: ({ row }) => {
          const count = row.original.participant_count || 0;
          const max = row.original.max_participants;
          return (
            <div className="text-center">
              <div className="font-medium">
                {count}
                {max ? ` / ${max}` : ''}
              </div>
              {row.original.completion_rate !== undefined && (
                <div className="text-sm text-gray-500">
                  {Math.round(row.original.completion_rate)}% {t('courses.list.columns.completion')}
                </div>
              )}
            </div>
          );
        },
      },
      {
        accessorKey: 'instructor_name',
        header: t('courses.list.columns.instructor'),
        cell: ({ row }) => row.original.instructor_name || '-',
      },
      {
        id: 'actions',
        header: t('common.actions'),
        enableSorting: false,
        cell: ({ row }) => (
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate(`/courses/${row.original.id}`)}
            >
              <Eye className="h-4 w-4" />
            </Button>
            {canEdit(row.original) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate(`/courses/${row.original.id}/edit`)}
              >
                <Edit className="h-4 w-4" />
              </Button>
            )}
            {canCreate && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDuplicate(row.original)}
                title={t('courses.list.copyCourse')}
              >
                <Copy className="h-4 w-4" />
              </Button>
            )}
            {canDelete && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() =>
                  setDeleteConfirm({ isOpen: true, course: row.original })
                }
                className="text-red-600 hover:text-red-800"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        ),
      },
    ],
    [navigate, canCreate, canDelete, user?.id]
  );

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">
          {t('courses.form.messages.loadError')}
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('courses.title')}</h1>
          <p className="text-gray-600 mt-1">
            {t('courses.subtitle')}
          </p>
        </div>
        {canCreate && (
          <Button onClick={() => navigate('/courses/new')}>
            <Plus className="h-4 w-4 mr-2" />
            {t('courses.list.newCourse')}
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card className="p-6">
        <div className="space-y-4">
          {/* Search */}
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder={t('courses.list.searchPlaceholder')}
                  value={search}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="h-4 w-4 mr-2" />
              {t('common.filters')}
            </Button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t">
              <Select
                placeholder={t('courses.list.filters.selectProgram')}
                value={filters.program_id?.toString() || ''}
                onChange={(value) =>
                  handleFilterChange(
                    'program_id',
                    value ? parseInt(value) : undefined
                  )
                }
                options={[
                  { value: '', label: t('courses.list.filters.allPrograms') },
                  ...(programsData?.programs || []).map((program) => ({
                    value: program.id.toString(),
                    label: program.title,
                  })),
                ]}
              />
              <Select
                placeholder={t('courses.list.filters.selectStatus')}
                value={filters.status || ''}
                onChange={(value) => handleFilterChange('status', value)}
                options={[
                  { value: '', label: t('courses.list.filters.allStatuses') },
                  ...COURSE_STATUS_OPTIONS.map((option) => ({
                    value: option.value,
                    label: option.label,
                  })),
                ]}
              />
              <Select
                placeholder={t('courses.list.filters.selectFormat')}
                value={filters.format || ''}
                onChange={(value) => handleFilterChange('format', value)}
                options={[
                  { value: '', label: t('courses.list.filters.allFormats') },
                  ...COURSE_FORMAT_OPTIONS.map((option) => ({
                    value: option.value,
                    label: option.label,
                  })),
                ]}
              />
              <Select
                placeholder={t('courses.list.filters.selectDifficulty')}
                value={filters.difficulty || ''}
                onChange={(value) => handleFilterChange('difficulty', value)}
                options={[
                  { value: '', label: t('courses.list.filters.allLevels') },
                  ...DIFFICULTY_LEVEL_OPTIONS.map((option) => ({
                    value: option.value,
                    label: option.label,
                  })),
                ]}
              />
            </div>
          )}
        </div>
      </Card>

      {/* Statistics Cards */}
      {data?.courses && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="text-2xl font-bold text-blue-600">
              {data.courses.length}
            </div>
            <div className="text-sm text-gray-600">{t('courses.list.stats.totalCourses')}</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-green-600">
              {data.courses.filter((c) => c.status === 'published').length}
            </div>
            <div className="text-sm text-gray-600">{t('courses.list.stats.published')}</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-yellow-600">
              {data.courses.filter((c) => c.status === 'draft').length}
            </div>
            <div className="text-sm text-gray-600">{t('courses.list.stats.draft')}</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-purple-600">
              {data.courses.filter((c) => c.has_assessment).length}
            </div>
            <div className="text-sm text-gray-600">{t('courses.list.stats.withAssessment')}</div>
          </Card>
        </div>
      )}

      {/* Table */}
      <Card>
        {isLoading ? (
          <DataTableSkeleton columns={9} rows={10} showPagination />
        ) : data?.courses && data.courses.length === 0 ? (
          <EmptyState
            icon={GraduationCap}
            title={t('courses.list.noCourses')}
            description={t('courses.list.noCoursesDescription')}
            action={
              canCreate
                ? {
                    text: t('courses.list.createNewCourse'),
                    onClick: () => navigate('/courses/new'),
                  }
                : undefined
            }
          />
        ) : (
          <DataTable
            columns={columns}
            data={data?.courses || []}
            pagination={{
              pageIndex: (filters.page || 1) - 1,
              pageSize: filters.per_page || 20,
              pageCount: data?.pagination?.pages || 1,
              total: data?.pagination?.total || 0,
            }}
            onPaginationChange={(pagination) => {
              handlePageChange(pagination.pageIndex + 1);
            }}
            sorting={sorting}
            onSortingChange={setSorting}
            loading={isLoading}
          />
        )}
      </Card>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        onClose={() => setDeleteConfirm({ isOpen: false })}
        onConfirm={() =>
          deleteConfirm.course && handleDelete(deleteConfirm.course)
        }
        title={t('courses.form.messages.deleteConfirmTitle')}
        description={t('courses.form.messages.deleteConfirmMessage', { name: deleteConfirm.course?.title })}
        confirmText={t('common.delete')}
        cancelText={t('common.cancel')}
        loading={deleteCourse.isPending}
      />
    </div>
  );
};

export default CourseList;
