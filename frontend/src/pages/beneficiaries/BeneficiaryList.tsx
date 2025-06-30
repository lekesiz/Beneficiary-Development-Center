import { ColumnDef, PaginationState, SortingState } from '@tanstack/react-table';
import {
  MoreHorizontal,
  Plus,
  Eye,
  Edit,
  Trash2,
  Tag,
  UserPlus,
  FileText,
  Download,
  Filter,
  Users,
} from 'lucide-react';
import { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import { DataTableSkeleton } from '@/components/common/DataTableSkeleton';
import { DataTable } from '@/components/ui/DataTable';
import { EmptyState } from '@/components/ui/EmptyState';
import { useAuth } from '@/contexts/AuthContext';
import { useBeneficiaries, useDeleteBeneficiary } from '@/hooks/useBeneficiaries';
import { formatDate, debounce } from '@/lib/utils';
import { Beneficiary, BeneficiaryStatus } from '@/types/beneficiary';

export default function BeneficiaryList() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { t } = useTranslation();
  const [globalFilter, setGlobalFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<BeneficiaryStatus | ''>(
    BeneficiaryStatus.ACTIVE
  );
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 20,
  });
  const [sorting, setSorting] = useState<SortingState>([{ id: 'created_at', desc: true }]);

  // Debounced search
  const debouncedSearch = useMemo(
    () =>
      debounce((value: string) => {
        setPagination((prev) => ({ ...prev, pageIndex: 0 }));
      }, 500),
    []
  );

  const handleSearchChange = (value: string) => {
    setGlobalFilter(value);
    debouncedSearch(value);
  };

  // Query parameters
  const queryParams = useMemo(
    () => ({
      page: pagination.pageIndex + 1,
      per_page: pagination.pageSize,
      search: globalFilter || undefined,
      status: statusFilter || undefined,
      sort_by: sorting[0]?.id as any,
      sort_order: sorting[0]?.desc ? 'desc' : ('asc' as any),
    }),
    [pagination, globalFilter, statusFilter, sorting]
  );

  const { data, isLoading } = useBeneficiaries(queryParams);
  const deleteMutation = useDeleteBeneficiary();

  const columns: ColumnDef<Beneficiary>[] = [
    {
      accessorKey: 'full_name',
      header: t('beneficiaries.list.columns.name'),
      enableSorting: true,
      cell: ({ row }) => {
        const beneficiary = row.original;
        return (
          <div>
            <div className="font-medium">{beneficiary.full_name}</div>
            {beneficiary.email && (
              <div className="text-sm text-muted-foreground">{beneficiary.email}</div>
            )}
          </div>
        );
      },
    },
    {
      accessorKey: 'phone',
      header: t('beneficiaries.list.columns.phone'),
      cell: ({ row }) => row.original.phone || row.original.mobile_phone || '-',
    },
    {
      accessorKey: 'status',
      header: t('beneficiaries.list.columns.status'),
      enableSorting: true,
      cell: ({ row }) => {
        const status = row.original.status;
        const statusColors = {
          [BeneficiaryStatus.ACTIVE]: 'bg-green-100 text-green-800',
          [BeneficiaryStatus.INACTIVE]: 'bg-gray-100 text-gray-800',
          [BeneficiaryStatus.COMPLETED]: 'bg-blue-100 text-blue-800',
          [BeneficiaryStatus.SUSPENDED]: 'bg-red-100 text-red-800',
        };

        return (
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[status]}`}
          >
            {status}
          </span>
        );
      },
    },
    {
      accessorKey: 'assigned_trainer_name',
      header: t('beneficiaries.list.columns.trainer'),
      cell: ({ row }) => row.original.assigned_trainer_name || '-',
    },
    {
      accessorKey: 'tags',
      header: t('beneficiaries.list.columns.tags'),
      cell: ({ row }) => {
        const tags = row.original.tags;
        if (!tags || tags.length === 0) return '-';

        return (
          <div className="flex flex-wrap gap-1">
            {tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/10 text-primary"
              >
                {tag}
              </span>
            ))}
            {tags.length > 3 && (
              <span className="text-xs text-muted-foreground">+{tags.length - 3}</span>
            )}
          </div>
        );
      },
    },
    {
      accessorKey: 'created_at',
      header: t('beneficiaries.list.columns.created'),
      enableSorting: true,
      cell: ({ row }) => formatDate(row.original.created_at),
    },
    {
      id: 'actions',
      header: t('beneficiaries.list.columns.actions'),
      cell: ({ row }) => {
        const beneficiary = row.original;
        const canEdit = user?.role === 'admin' || user?.role === 'trainer';
        const canDelete = user?.role === 'admin';

        return (
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate(`/beneficiaries/${beneficiary.id}`)}
              className="p-1 hover:bg-accent rounded"
              title={t('beneficiaries.list.actions.viewDetails')}
            >
              <Eye className="h-4 w-4" />
            </button>

            {canEdit && (
              <button
                onClick={() => navigate(`/beneficiaries/${beneficiary.id}/edit`)}
                className="p-1 hover:bg-accent rounded"
                title={t('beneficiaries.list.actions.edit')}
              >
                <Edit className="h-4 w-4" />
              </button>
            )}

            {canDelete && (
              <button
                onClick={() => {
                  if (confirm(t('beneficiaries.list.actions.deleteConfirm'))) {
                    deleteMutation.mutate(beneficiary.id);
                  }
                }}
                className="p-1 hover:bg-accent rounded text-destructive"
                title={t('beneficiaries.list.actions.delete')}
              >
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        );
      },
    },
  ];

  const canCreate = user?.role === 'admin' || user?.role === 'trainer';

  return (
    <div className="container mx-auto py-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{t('beneficiaries.title')}</h1>
            <p className="text-muted-foreground">{t('beneficiaries.subtitle')}</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                /* TODO: Export functionality */
              }}
              className="inline-flex items-center px-4 py-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md text-sm font-medium"
            >
              <Download className="h-4 w-4 mr-2" />
              {t('common.export')}
            </button>

            {canCreate && (
              <button
                onClick={() => navigate('/beneficiaries/new')}
                className="inline-flex items-center px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90 rounded-md text-sm font-medium"
              >
                <Plus className="h-4 w-4 mr-2" />
                {t('beneficiaries.list.addBeneficiary')}
              </button>
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 max-w-sm">
            <input
              placeholder={t('beneficiaries.list.searchPlaceholder')}
              value={globalFilter}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="w-full px-3 py-2 text-sm border rounded-md border-input bg-background"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as BeneficiaryStatus | '')}
            className="px-3 py-2 text-sm border rounded-md border-input bg-background"
          >
            <option value="">{t('beneficiaries.list.filters.allStatus')}</option>
            <option value={BeneficiaryStatus.ACTIVE}>{t('beneficiaries.statuses.active')}</option>
            <option value={BeneficiaryStatus.INACTIVE}>
              {t('beneficiaries.statuses.inactive')}
            </option>
            <option value={BeneficiaryStatus.COMPLETED}>
              {t('beneficiaries.statuses.completed')}
            </option>
            <option value={BeneficiaryStatus.SUSPENDED}>
              {t('beneficiaries.statuses.suspended')}
            </option>
          </select>

          <button
            onClick={() => {
              /* TODO: Advanced filters */
            }}
            className="inline-flex items-center px-3 py-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md text-sm font-medium"
          >
            <Filter className="h-4 w-4 mr-2" />
            {t('beneficiaries.list.filters.moreFilters')}
          </button>
        </div>

        {/* Data Table */}
        {isLoading ? (
          <DataTableSkeleton columns={7} rows={10} showPagination />
        ) : data?.data.beneficiaries &&
          data.data.beneficiaries.length === 0 &&
          !globalFilter &&
          !statusFilter ? (
          <div className="bg-white rounded-lg border">
            <EmptyState
              icon={Users}
              title={t('beneficiaries.list.noBeneficiaries')}
              description={t('beneficiaries.list.noBeneficiariesDescription')}
              action={
                canCreate
                  ? {
                      text: t('beneficiaries.list.addNewBeneficiary'),
                      onClick: () => navigate('/beneficiaries/new'),
                    }
                  : undefined
              }
            />
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={data?.data.beneficiaries || []}
            loading={isLoading}
            pageCount={data?.data.pagination?.pages}
            pagination={pagination}
            onPaginationChange={setPagination}
            sorting={sorting}
            onSortingChange={setSorting}
          />
        )}
      </div>
    </div>
  );
}
