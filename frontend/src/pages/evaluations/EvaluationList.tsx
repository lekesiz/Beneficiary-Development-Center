import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { ColumnDef, PaginationState, SortingState } from '@tanstack/react-table';
import { 
  Eye, 
  Edit, 
  Trash2, 
  Plus, 
  Play, 
  Archive, 
  MoreHorizontal,
  Clock,
  Users,
  FileText,
  Filter,
  Brain,
  BookOpen,
  Target,
  Trophy
} from 'lucide-react';
import { DataTable } from '@/components/ui/DataTable';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Modal } from '@/components/ui/Modal';
import { 
  useEvaluations, 
  useDeleteEvaluation, 
  useActivateEvaluation, 
  useArchiveEvaluation,
  useEvaluationStatistics 
} from '@/hooks/useEvaluations';
import type { Evaluation, EvaluationFilters } from '@/types/evaluation';

// Status badge component
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const variants = {
    draft: 'secondary',
    active: 'success',
    archived: 'warning',
    completed: 'default'
  } as const;

  const labels = {
    draft: 'Taslak',
    active: 'Aktif',
    archived: 'Arşivlenmiş',
    completed: 'Tamamlanmış'
  };

  return (
    <Badge variant={variants[status as keyof typeof variants] || 'secondary'}>
      {labels[status as keyof typeof labels] || status}
    </Badge>
  );
};

// Actions dropdown component
const ActionsDropdown: React.FC<{ 
  evaluation: Evaluation; 
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
  onActivate: (id: number) => void;
  onArchive: (id: number) => void;
  onView: (id: number) => void;
}> = ({ evaluation, onEdit, onDelete, onActivate, onArchive, onView }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 hover:bg-gray-100 rounded-md"
      >
        <MoreHorizontal className="h-4 w-4" />
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white border rounded-md shadow-lg z-10">
          <button
            onClick={() => { onView(evaluation.id); setIsOpen(false); }}
            className="flex items-center w-full px-4 py-2 text-sm hover:bg-gray-100"
          >
            <Eye className="mr-2 h-4 w-4" />
            Görüntüle
          </button>
          <button
            onClick={() => { onEdit(evaluation.id); setIsOpen(false); }}
            className="flex items-center w-full px-4 py-2 text-sm hover:bg-gray-100"
          >
            <Edit className="mr-2 h-4 w-4" />
            Düzenle
          </button>
          {evaluation.status === 'draft' && (
            <button
              onClick={() => { onActivate(evaluation.id); setIsOpen(false); }}
              className="flex items-center w-full px-4 py-2 text-sm hover:bg-gray-100"
            >
              <Play className="mr-2 h-4 w-4" />
              Aktifleştir
            </button>
          )}
          {evaluation.status === 'active' && (
            <button
              onClick={() => { onArchive(evaluation.id); setIsOpen(false); }}
              className="flex items-center w-full px-4 py-2 text-sm hover:bg-gray-100"
            >
              <Archive className="mr-2 h-4 w-4" />
              Arşivle
            </button>
          )}
          <hr className="my-1" />
          <button
            onClick={() => { onDelete(evaluation.id); setIsOpen(false); }}
            className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Sil
          </button>
        </div>
      )}
    </div>
  );
};

// Filters component
const EvaluationFilters: React.FC<{
  filters: EvaluationFilters;
  onFiltersChange: (filters: EvaluationFilters) => void;
}> = ({ filters, onFiltersChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center px-4 py-2 border rounded-md hover:bg-gray-50"
      >
        <Filter className="mr-2 h-4 w-4" />
        Filtrele
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white border rounded-md shadow-lg z-10 p-4">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Durum</label>
              <select
                value={filters.status || ''}
                onChange={(e) => onFiltersChange({ ...filters, status: e.target.value || undefined })}
                className="w-full p-2 border rounded-md"
              >
                <option value="">Tümü</option>
                <option value="draft">Taslak</option>
                <option value="active">Aktif</option>
                <option value="archived">Arşivlenmiş</option>
                <option value="completed">Tamamlanmış</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Sıralama</label>
              <select
                value={filters.sort_by || 'created_at'}
                onChange={(e) => onFiltersChange({ ...filters, sort_by: e.target.value })}
                className="w-full p-2 border rounded-md"
              >
                <option value="created_at">Oluşturulma Tarihi</option>
                <option value="title">Başlık</option>
                <option value="total_questions">Soru Sayısı</option>
                <option value="passing_score">Geçme Puanı</option>
              </select>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="sort_desc"
                checked={filters.sort_desc || false}
                onChange={(e) => onFiltersChange({ ...filters, sort_desc: e.target.checked })}
                className="mr-2"
              />
              <label htmlFor="sort_desc" className="text-sm">Azalan sıralama</label>
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t">
            <button
              onClick={() => setIsOpen(false)}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Uygula
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default function EvaluationList() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<EvaluationFilters>({
    page: 1,
    per_page: 20,
    sort_by: 'created_at',
    sort_desc: true
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteModal, setDeleteModal] = useState<{ isOpen: boolean; evaluationId?: number }>({
    isOpen: false
  });

  // React Query hooks
  const { data: evaluationsData, isLoading, error } = useEvaluations({
    ...filters,
    search: searchTerm || undefined
  });
  const { data: statistics } = useEvaluationStatistics();
  const deleteMutation = useDeleteEvaluation();
  const activateMutation = useActivateEvaluation();
  const archiveMutation = useArchiveEvaluation();

  // Pagination state
  const pagination: PaginationState = {
    pageIndex: (filters.page || 1) - 1,
    pageSize: filters.per_page || 20
  };

  // Sorting state
  const sorting: SortingState = filters.sort_by ? [{
    id: filters.sort_by,
    desc: filters.sort_desc || false
  }] : [];

  // Table columns
  const columns: ColumnDef<Evaluation>[] = useMemo(() => [
    {
      accessorKey: 'title',
      header: 'Başlık',
      cell: ({ row }) => (
        <div className="flex flex-col">
          <div className="flex items-center space-x-2">
            <span className="font-medium">{row.original.title}</span>
            {row.original.is_adaptive && (
              <Badge 
                variant="outline" 
                className="bg-purple-50 text-purple-700 border-purple-200"
              >
                <Brain className="mr-1 h-3 w-3" />
                AI Adaptif
              </Badge>
            )}
          </div>
          {row.original.description && (
            <span className="text-sm text-gray-500 truncate max-w-xs">
              {row.original.description}
            </span>
          )}
        </div>
      )
    },
    {
      accessorKey: 'status',
      header: 'Durum',
      cell: ({ row }) => <StatusBadge status={row.original.status} />
    },
    {
      accessorKey: 'total_questions',
      header: 'Soru Sayısı',
      cell: ({ row }) => (
        <div className="flex items-center">
          <FileText className="mr-1 h-4 w-4 text-gray-400" />
          {row.original.total_questions}
        </div>
      )
    },
    {
      accessorKey: 'total_points',
      header: 'Toplam Puan',
      cell: ({ row }) => row.original.total_points.toFixed(1)
    },
    {
      accessorKey: 'passing_score',
      header: 'Geçme Puanı',
      cell: ({ row }) => `${row.original.passing_score}%`
    },
    {
      accessorKey: 'duration_display',
      header: 'Süre',
      cell: ({ row }) => (
        <div className="flex items-center">
          <Clock className="mr-1 h-4 w-4 text-gray-400" />
          {row.original.duration_display}
        </div>
      )
    },
    {
      accessorKey: 'is_available',
      header: 'Kullanılabilirlik',
      cell: ({ row }) => (
        <Badge variant={row.original.is_available ? 'success' : 'secondary'}>
          {row.original.is_available ? 'Mevcut' : 'Mevcut Değil'}
        </Badge>
      )
    },
    {
      accessorKey: 'created_at',
      header: 'Oluşturulma',
      cell: ({ row }) => new Date(row.original.created_at).toLocaleDateString('tr-TR')
    },
    {
      id: 'actions',
      header: 'İşlemler',
      cell: ({ row }) => (
        <ActionsDropdown
          evaluation={row.original}
          onView={(id) => navigate(`/evaluations/${id}`)}
          onEdit={(id) => navigate(`/evaluations/${id}/edit`)}
          onDelete={(id) => setDeleteModal({ isOpen: true, evaluationId: id })}
          onActivate={(id) => activateMutation.mutate(id)}
          onArchive={(id) => archiveMutation.mutate(id)}
        />
      )
    }
  ], [navigate, activateMutation, archiveMutation]);

  // Handle pagination change
  const handlePaginationChange = (newPagination: PaginationState) => {
    setFilters(prev => ({
      ...prev,
      page: newPagination.pageIndex + 1,
      per_page: newPagination.pageSize
    }));
  };

  // Handle sorting change
  const handleSortingChange = (newSorting: SortingState) => {
    const sort = newSorting[0];
    setFilters(prev => ({
      ...prev,
      sort_by: sort?.id,
      sort_desc: sort?.desc
    }));
  };

  // Handle delete
  const handleDelete = () => {
    if (deleteModal.evaluationId) {
      deleteMutation.mutate(deleteModal.evaluationId);
      setDeleteModal({ isOpen: false });
    }
  };

  if (error) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <p className="text-red-600">Değerlendirmeler yüklenirken hata oluştu.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Değerlendirmeler</h1>
          <p className="text-gray-600">Değerlendirmeleri yönetin ve izleyin</p>
        </div>
        <button
          onClick={() => navigate('/evaluations/create')}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <Plus className="mr-2 h-4 w-4" />
          Yeni Değerlendirme
        </button>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Toplam Değerlendirme</p>
                <p className="text-2xl font-bold">{statistics.total_evaluations}</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center">
              <Play className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Aktif Değerlendirmeler</p>
                <p className="text-2xl font-bold">{statistics.active_evaluations}</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Toplam Deneme</p>
                <p className="text-2xl font-bold">{statistics.total_attempts}</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <span className="text-yellow-600 font-bold">%</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Ortalama Başarı</p>
                <p className="text-2xl font-bold">{statistics.average_score.toFixed(1)}%</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Filters and Search */}
      <div className="flex justify-between items-center">
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Değerlendirmelerde ara..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border rounded-md"
          />
        </div>
        <EvaluationFilters
          filters={filters}
          onFiltersChange={setFilters}
        />
      </div>

      {/* Data Table */}
      <Card>
        <DataTable
          columns={columns}
          data={evaluationsData?.evaluations || []}
          loading={isLoading}
          pageCount={evaluationsData?.pagination.pages}
          pagination={pagination}
          onPaginationChange={handlePaginationChange}
          sorting={sorting}
          onSortingChange={handleSortingChange}
        />
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false })}
        title="Değerlendirmeyi Sil"
      >
        <div className="space-y-4">
          <p>Bu değerlendirmeyi silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.</p>
          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setDeleteModal({ isOpen: false })}
              className="px-4 py-2 border rounded-md hover:bg-gray-50"
            >
              İptal
            </button>
            <button
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
            >
              {deleteMutation.isPending ? <LoadingSpinner size="sm" /> : 'Sil'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}