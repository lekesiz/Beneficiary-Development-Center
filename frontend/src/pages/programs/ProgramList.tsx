/**
 * Program List Page
 */
import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { usePrograms, useDeleteProgram } from '../../hooks/usePrograms';
import { useAuth } from '../../hooks/useAuth';
import { DataTable } from '../../components/ui/DataTable';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Input } from '../../components/ui/Input';
import { Select } from '../../components/ui/Select';
import { Card } from '../../components/ui/Card';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { formatProgramDate, getProgramStatusInfo, getProgramTypeInfo, formatProgramPrice } from '../../utils/program';
import { PROGRAM_STATUS_OPTIONS, PROGRAM_TYPE_OPTIONS } from '../../constants/program';
import type { Program, ProgramFilters } from '../../types/program';
import type { ColumnDef } from '@tanstack/react-table';
import { Edit, Eye, Trash2, Plus, Search, Filter } from 'lucide-react';

export const ProgramList: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const deleteProgram = useDeleteProgram();

  // Filters state
  const [filters, setFilters] = useState<ProgramFilters>({
    page: 1,
    per_page: 20,
  });
  const [search, setSearch] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; program?: Program }>({
    isOpen: false,
  });

  // Fetch programs
  const { data, isLoading, error } = usePrograms(filters);

  // Permission checks
  const canCreate = user?.role && ['admin', 'manager'].includes(user.role);
  const canEdit = user?.role && ['admin', 'manager'].includes(user.role);
  const canDelete = user?.role === 'admin';

  // Handle search
  const handleSearch = (value: string) => {
    setSearch(value);
    setFilters(prev => ({
      ...prev,
      search: value || undefined,
      page: 1,
    }));
  };

  // Handle filter changes
  const handleFilterChange = (key: keyof ProgramFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value || undefined,
      page: 1,
    }));
  };

  // Handle pagination
  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
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
  const columns = useMemo<ColumnDef<Program>[]>(() => [
    {
      accessorKey: 'title',
      header: 'Program Adı',
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
      header: 'Tür',
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
      header: 'Durum',
      cell: ({ row }) => {
        const statusInfo = getProgramStatusInfo(row.original.status);
        return (
          <Badge color={statusInfo.color}>
            {statusInfo.label}
          </Badge>
        );
      },
    },
    {
      accessorKey: 'start_date',
      header: 'Başlangıç',
      cell: ({ row }) => formatProgramDate(row.original.start_date, 'dd MMM yyyy'),
    },
    {
      accessorKey: 'end_date',
      header: 'Bitiş',
      cell: ({ row }) => formatProgramDate(row.original.end_date, 'dd MMM yyyy'),
    },
    {
      accessorKey: 'enrollment_count',
      header: 'Katılımcı',
      cell: ({ row }) => (
        <div className="text-center">
          <div className="font-medium">
            {row.original.enrollment_count || 0} / {row.original.max_participants}
          </div>
          <div className="text-sm text-gray-500">
            {Math.round(((row.original.enrollment_count || 0) / row.original.max_participants) * 100)}%
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'price',
      header: 'Ücret',
      cell: ({ row }) => formatProgramPrice(row.original.price, row.original.currency),
    },
    {
      accessorKey: 'coordinator_name',
      header: 'Koordinatör',
      cell: ({ row }) => row.original.coordinator_name || '-',
    },
    {
      id: 'actions',
      header: 'İşlemler',
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
  ], [navigate, canEdit, canDelete]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">
          Programlar yüklenirken hata oluştu. Lütfen tekrar deneyin.
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Programlar</h1>
          <p className="text-gray-600 mt-1">
            Eğitim programlarını görüntüleyin ve yönetin
          </p>
        </div>
        {canCreate && (
          <Button onClick={() => navigate('/programs/new')}>
            <Plus className="h-4 w-4 mr-2" />
            Yeni Program
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
                  placeholder="Program adı, kod veya açıklama ile ara..."
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
              Filtreler
            </Button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t">
              <Select
                placeholder="Durum seçin"
                value={filters.status || ''}
                onChange={(value) => handleFilterChange('status', value)}
                options={[
                  { value: '', label: 'Tüm Durumlar' },
                  ...PROGRAM_STATUS_OPTIONS.map(option => ({
                    value: option.value,
                    label: option.label,
                  })),
                ]}
              />
              <Select
                placeholder="Tür seçin"
                value={filters.type || ''}
                onChange={(value) => handleFilterChange('type', value)}
                options={[
                  { value: '', label: 'Tüm Türler' },
                  ...PROGRAM_TYPE_OPTIONS.map(option => ({
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
                  Sadece Yaklaşan
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
                  Sadece Aktif
                </label>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Table */}
      <Card>
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
          loading={isLoading}
        />
      </Card>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        onClose={() => setDeleteConfirm({ isOpen: false })}
        onConfirm={() => deleteConfirm.program && handleDelete(deleteConfirm.program)}
        title="Programı Sil"
        description={`"${deleteConfirm.program?.title}" programını silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.`}
        confirmText="Sil"
        cancelText="İptal"
        loading={deleteProgram.isPending}
      />
    </div>
  );
};

export default ProgramList;