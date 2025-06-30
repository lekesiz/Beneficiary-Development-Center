/**
 * Program List Page
 */
import type { ColumnDef, SortingState } from '@tanstack/react-table';
import { Edit, Eye, Trash2, Plus, Search, Filter, BookOpen } from 'lucide-react';
import * as React from 'react';
import { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';

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
import { PROGRAM_STATUS_OPTIONS, PROGRAM_TYPE_OPTIONS } from '../../constants/program';
import { useAuth } from '../../contexts/AuthContext';
import { usePrograms, useDeleteProgram } from '../../hooks/usePrograms';
import type { Program, ProgramFilters } from '../../types/program';
import {
  formatProgramDate,
  getProgramStatusInfo,
  getProgramTypeInfo,
  formatProgramPrice,
} from '../../utils/program';

export const ProgramList: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { t } = useTranslation();
  const deleteProgram = useDeleteProgram();

  // Filters state
  const [filters, setFilters] = useState<ProgramFilters>({
    page: 1,
    per_page: 20,
  });
  const [search, setSearch] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    program?: Program;
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

  // Fetch programs
  const { data, isLoading, error } = usePrograms(filters);

  // Permission checks
  const canCreate = user?.roles?.some(role => ['admin', 'manager', 'trainer'].includes(role.name)) || 
                    user?.primaryRole && ['admin', 'manager', 'trainer'].includes(user.primaryRole);
  const canEdit = user?.roles?.some(role => ['admin', 'manager', 'trainer'].includes(role.name)) || 
                  user?.primaryRole && ['admin', 'manager', 'trainer'].includes(user.primaryRole);
  const canDelete = user?.roles?.some(role => ['admin'].includes(role.name)) || 
                    user?.primaryRole === 'admin';

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
  const handleFilterChange = (key: keyof ProgramFilters, value: any) => {
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
  const handleDelete = async (program: Program) => {
    try {
      await deleteProgram.mutateAsync(program.id);
      setDeleteConfirm({ isOpen: false });
    } catch (error) {
      // Error handled by mutation
    }
  };

  // Table columns
  const columns = useMemo<ColumnDef<Program>[]>(
    () => [
      {
        accessorKey: 'title',
        header: t('programs.list.columns.name'),
        enableSorting: true,
        cell: ({ row }) => (
          <div className="flex flex-col">
            <Link
              to={`/programs/${row.original.id}`}
              className="font-medium text-blue-600 hover:text-blue-800"
            >
              {row.original.title}
            </Link>
            <span className="text-sm text-gray-500">{row.original.code}</span>
          </div>
        ),
      },
      {
        accessorKey: 'program_type',
        header: t('programs.list.columns.type'),
        enableSorting: true,
        cell: ({ row }) => {
          const typeInfo = getProgramTypeInfo(row.original.program_type);
          return (
            <div className="flex items-center space-x-2">
              <span>{typeInfo.icon}</span>
              <span>{typeInfo.label}</span>
            </div>
          );
        },
      },
      {
        accessorKey: 'status',
        header: t('programs.list.columns.status'),
        enableSorting: true,
        cell: ({ row }) => {
          const statusInfo = getProgramStatusInfo(row.original.status);
          return <Badge color={statusInfo.color}>{statusInfo.label}</Badge>;
        },
      },
      {
        accessorKey: 'start_date',
        header: t('programs.list.columns.startDate'),
        enableSorting: true,
        cell: ({ row }) => formatProgramDate(row.original.start_date, 'dd MMM yyyy'),
      },
      {
        accessorKey: 'end_date',
        header: t('programs.list.columns.endDate'),
        enableSorting: true,
        cell: ({ row }) => formatProgramDate(row.original.end_date, 'dd MMM yyyy'),
      },
      {
        accessorKey: 'enrollment_count',
        header: t('programs.list.columns.participants'),
        cell: ({ row }) => (
          <div className="text-center">
            <div className="font-medium">
              {row.original.enrollment_count || 0} / {row.original.max_participants}
            </div>
            <div className="text-sm text-gray-500">
              {Math.round(
                ((row.original.enrollment_count || 0) / row.original.max_participants) * 100
              )}
              %
            </div>
          </div>
        ),
      },
      {
        accessorKey: 'price',
        header: t('programs.list.columns.price'),
        cell: ({ row }) => formatProgramPrice(row.original.price, row.original.currency),
      },
      {
        accessorKey: 'coordinator_name',
        header: t('programs.list.columns.coordinator'),
        cell: ({ row }) => row.original.coordinator_name || '-',
      },
      {
        accessorKey: 'created_at',
        header: t('programs.list.columns.createdAt'),
        enableSorting: true,
        cell: ({ row }) => formatProgramDate(row.original.created_at, 'dd MMM yyyy'),
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
              onClick={() => navigate(`/programs/${row.original.id}`)}
            >
              <Eye className="h-4 w-4" />
            </Button>
            {canEdit && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate(`/programs/${row.original.id}/edit`)}
              >
                <Edit className="h-4 w-4" />
              </Button>
            )}
            {canDelete && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDeleteConfirm({ isOpen: true, program: row.original })}
                className="text-red-600 hover:text-red-800"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        ),
      },
    ],
    [navigate, canEdit, canDelete]
  );

  // Remove the early return for loading state - we'll handle it inline

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">{t('errors.loadFailed')}</div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('programs.title')}</h1>
          <p className="text-gray-600 mt-1">{t('programs.subtitle')}</p>
        </div>
        {canCreate && (
          <Button onClick={() => navigate('/programs/new')}>
            <Plus className="h-4 w-4 mr-2" />
            {t('programs.list.newProgram')}
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
                  placeholder={t('programs.list.searchPlaceholder')}
                  value={search}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
              <Filter className="h-4 w-4 mr-2" />
              {t('common.filters')}
            </Button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t">
              <Select
                placeholder={t('programs.list.filters.allStatuses')}
                value={filters.status || ''}
                onChange={(value) => handleFilterChange('status', value)}
                options={[
                  { value: '', label: t('programs.list.filters.allStatuses') },
                  ...PROGRAM_STATUS_OPTIONS.map((option) => ({
                    value: option.value,
                    label: option.label,
                  })),
                ]}
              />
              <Select
                placeholder={t('programs.list.filters.allTypes')}
                value={filters.type || ''}
                onChange={(value) => handleFilterChange('type', value)}
                options={[
                  { value: '', label: t('programs.list.filters.allTypes') },
                  ...PROGRAM_TYPE_OPTIONS.map((option) => ({
                    value: option.value,
                    label: option.label,
                  })),
                ]}
              />
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="upcoming_only"
                  checked={filters.upcoming_only || false}
                  onChange={(e) => handleFilterChange('upcoming_only', e.target.checked)}
                  className="rounded border-gray-300"
                />
                <label htmlFor="upcoming_only" className="text-sm">
                  {t('programs.list.filters.upcomingOnly')}
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="active_only"
                  checked={filters.active_only || false}
                  onChange={(e) => handleFilterChange('active_only', e.target.checked)}
                  className="rounded border-gray-300"
                />
                <label htmlFor="active_only" className="text-sm">
                  {t('programs.list.filters.activeOnly')}
                </label>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Table */}
      <Card>
        {isLoading ? (
          <DataTableSkeleton columns={5} rows={10} showPagination />
        ) : data?.programs && data.programs.length === 0 ? (
          <EmptyState
            icon={BookOpen}
            title={t('programs.list.noPrograms')}
            description={t('programs.list.noProgramsDescription')}
            action={
              canCreate
                ? {
                    text: t('programs.list.createNewProgram'),
                    onClick: () => navigate('/programs/new'),
                  }
                : undefined
            }
          />
        ) : (
          <DataTable
            columns={columns}
            data={data?.programs || []}
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
        onConfirm={() => deleteConfirm.program && handleDelete(deleteConfirm.program)}
        title={t('programs.form.messages.deleteConfirmTitle')}
        description={t('programs.form.messages.deleteConfirmMessage', {
          name: deleteConfirm.program?.title,
        })}
        confirmText={t('common.delete')}
        cancelText={t('common.cancel')}
        loading={deleteProgram.isPending}
      />
    </div>
  );
};

export default ProgramList;
