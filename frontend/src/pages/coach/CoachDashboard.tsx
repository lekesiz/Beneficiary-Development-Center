import {
  Users,
  Filter,
  Download,
  Search,
  AlertCircle,
  TrendingUp,
  Shield,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  SortAsc,
  SortDesc,
} from 'lucide-react';
import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

import { DevelopmentReport } from '@/components/reports/DevelopmentReport';
import { StudentReportRow } from '@/components/reports/StudentReportRow';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/contexts/AuthContext';
import { useCourses } from '@/hooks/useCourses';
import { usePrograms } from '@/hooks/usePrograms';
import {
  useReportsOverview,
  useExportBatchReports,
  type ReportsOverviewFilters,
} from '@/hooks/useReportsOverview';

export default function CoachDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [selectedStudents, setSelectedStudents] = useState<number[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  // Filters state
  const [filters, setFilters] = useState<ReportsOverviewFilters>({
    page: 1,
    per_page: 20,
    sort_by: 'risk_score',
    sort_desc: true,
  });

  // Temporary filter values
  const [tempFilters, setTempFilters] = useState<ReportsOverviewFilters>({});

  // Fetch data
  const { data: overview, isLoading, refetch } = useReportsOverview(filters);
  const { data: programs } = usePrograms();
  const { data: courses } = useCourses();
  const exportMutation = useExportBatchReports();

  // Check permissions
  const hasAccess =
    user && ['admin', 'manager', 'instructor', 'trainer'].includes(user.role);

  if (!hasAccess) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">
            Bu sayfaya erişim yetkiniz bulunmamaktadır.
          </p>
          <Button onClick={() => navigate('/dashboard')} className="mt-4">
            Ana Sayfaya Dön
          </Button>
        </div>
      </div>
    );
  }

  // Statistics
  const statistics = useMemo(() => {
    if (!overview) return null;

    const summaries = overview.summaries;
    const highRisk = summaries.filter((s) => s.risk_score === 'High').length;
    const mediumRisk = summaries.filter(
      (s) => s.risk_score === 'Medium'
    ).length;
    const lowRisk = summaries.filter((s) => s.risk_score === 'Low').length;
    const avgPerformance =
      summaries.length > 0
        ? summaries.reduce((sum, s) => sum + s.performance_index, 0) /
          summaries.length
        : 0;

    return {
      total: summaries.length,
      highRisk,
      mediumRisk,
      lowRisk,
      avgPerformance: Math.round(avgPerformance),
      needsAttention: summaries.filter((s) => s.needs_attention).length,
    };
  }, [overview]);

  // Handlers
  const handleSelectAll = (checked: boolean) => {
    if (checked && overview) {
      setSelectedStudents(overview.summaries.map((s) => s.student_id));
    } else {
      setSelectedStudents([]);
    }
  };

  const handleSelectStudent = (studentId: number, selected: boolean) => {
    if (selected) {
      setSelectedStudents([...selectedStudents, studentId]);
    } else {
      setSelectedStudents(selectedStudents.filter((id) => id !== studentId));
    }
  };

  const handleApplyFilters = () => {
    setFilters({ ...filters, ...tempFilters, page: 1 });
    setShowFilters(false);
  };

  const handleResetFilters = () => {
    setTempFilters({});
    setFilters({
      page: 1,
      per_page: 20,
      sort_by: 'risk_score',
      sort_desc: true,
    });
    setShowFilters(false);
  };

  const handleSort = (field: 'risk_score' | 'performance' | 'name') => {
    if (filters.sort_by === field) {
      setFilters({ ...filters, sort_desc: !filters.sort_desc });
    } else {
      setFilters({ ...filters, sort_by: field, sort_desc: true });
    }
  };

  const handleExport = async () => {
    if (selectedStudents.length === 0) {
      alert('Lütfen dışa aktarmak için en az bir öğrenci seçin.');
      return;
    }

    try {
      await exportMutation.mutateAsync({
        student_ids: selectedStudents,
        format: 'json',
      });
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const handleViewDetails = (studentId: number) => {
    navigate(`/coach/student/${studentId}`);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center">
            <Users className="mr-2 h-6 w-6" />
            Öğrenci Gelişim Raporları
          </h1>
          <p className="text-gray-600 mt-1">
            Tüm öğrencilerin performans ve risk analizlerini görüntüleyin
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Yenile
          </Button>
          <Button
            variant="outline"
            onClick={handleExport}
            disabled={selectedStudents.length === 0 || exportMutation.isPending}
          >
            <Download className="mr-2 h-4 w-4" />
            Dışa Aktar ({selectedStudents.length})
          </Button>
        </div>
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Toplam Öğrenci
                </p>
                <p className="text-2xl font-bold">{statistics.total}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600 opacity-80" />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Ortalama Performans
                </p>
                <p className="text-2xl font-bold">
                  {statistics.avgPerformance}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600 opacity-80" />
            </div>
          </Card>

          <Card className="p-4 border-red-200 bg-red-50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-800">Yüksek Risk</p>
                <p className="text-2xl font-bold text-red-600">
                  {statistics.highRisk}
                </p>
              </div>
              <AlertCircle className="h-8 w-8 text-red-600 opacity-80" />
            </div>
          </Card>

          <Card className="p-4 border-yellow-200 bg-yellow-50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-yellow-800">Orta Risk</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {statistics.mediumRisk}
                </p>
              </div>
              <Shield className="h-8 w-8 text-yellow-600 opacity-80" />
            </div>
          </Card>

          <Card className="p-4 border-green-200 bg-green-50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-800">Düşük Risk</p>
                <p className="text-2xl font-bold text-green-600">
                  {statistics.lowRisk}
                </p>
              </div>
              <Shield className="h-8 w-8 text-green-600 opacity-80" />
            </div>
          </Card>
        </div>
      )}

      {/* Filters Bar */}
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Öğrenci ara..."
                value={tempFilters.search || ''}
                onChange={(e) =>
                  setTempFilters({ ...tempFilters, search: e.target.value })
                }
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleApplyFilters();
                  }
                }}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Filter Button */}
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className={showFilters ? 'bg-blue-50' : ''}
            >
              <Filter className="mr-2 h-4 w-4" />
              Filtreler
              {Object.keys(tempFilters).length > 0 && (
                <Badge variant="primary" size="sm" className="ml-2">
                  {Object.keys(tempFilters).length}
                </Badge>
              )}
            </Button>

            {/* Active Filters */}
            {filters.risk && (
              <Badge variant="outline">Risk: {filters.risk}</Badge>
            )}
            {filters.program_id && programs && (
              <Badge variant="outline">
                Program:{' '}
                {
                  programs.programs.find((p) => p.id === filters.program_id)
                    ?.title
                }
              </Badge>
            )}
          </div>

          {/* Results Count */}
          <div className="text-sm text-gray-600">
            {overview && `${overview.pagination.total} sonuç bulundu`}
          </div>
        </div>

        {/* Expanded Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Risk Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Risk Seviyesi
              </label>
              <select
                value={tempFilters.risk || ''}
                onChange={(e) =>
                  setTempFilters({
                    ...tempFilters,
                    risk: e.target.value as any,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Tümü</option>
                <option value="High">Yüksek</option>
                <option value="Medium">Orta</option>
                <option value="Low">Düşük</option>
              </select>
            </div>

            {/* Performance Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Performans Aralığı
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  min="0"
                  max="100"
                  placeholder="Min"
                  value={tempFilters.min_performance || ''}
                  onChange={(e) =>
                    setTempFilters({
                      ...tempFilters,
                      min_performance: e.target.value
                        ? Number(e.target.value)
                        : undefined,
                    })
                  }
                  className="w-20 px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <span>-</span>
                <input
                  type="number"
                  min="0"
                  max="100"
                  placeholder="Max"
                  value={tempFilters.max_performance || ''}
                  onChange={(e) =>
                    setTempFilters({
                      ...tempFilters,
                      max_performance: e.target.value
                        ? Number(e.target.value)
                        : undefined,
                    })
                  }
                  className="w-20 px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Program Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Program
              </label>
              <select
                value={tempFilters.program_id || ''}
                onChange={(e) =>
                  setTempFilters({
                    ...tempFilters,
                    program_id: e.target.value
                      ? Number(e.target.value)
                      : undefined,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Tüm Programlar</option>
                {programs?.programs.map((program) => (
                  <option key={program.id} value={program.id}>
                    {program.title}
                  </option>
                ))}
              </select>
            </div>

            {/* Filter Actions */}
            <div className="md:col-span-3 flex justify-end space-x-2">
              <Button variant="outline" onClick={handleResetFilters}>
                Temizle
              </Button>
              <Button onClick={handleApplyFilters}>Uygula</Button>
            </div>
          </div>
        )}
      </Card>

      {/* Students Table */}
      {isLoading ? (
        <Card className="p-12">
          <div className="flex justify-center">
            <LoadingSpinner size="lg" />
          </div>
        </Card>
      ) : overview && overview.summaries.length > 0 ? (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={
                        selectedStudents.length === overview.summaries.length
                      }
                      onChange={(e) => handleSelectAll(e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                  </th>
                  <th
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                    onClick={() => handleSort('name')}
                  >
                    <div className="flex items-center">
                      Öğrenci
                      {filters.sort_by === 'name' &&
                        (filters.sort_desc ? (
                          <SortDesc className="ml-1 h-4 w-4" />
                        ) : (
                          <SortAsc className="ml-1 h-4 w-4" />
                        ))}
                    </div>
                  </th>
                  <th
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                    onClick={() => handleSort('performance')}
                  >
                    <div className="flex items-center">
                      Performans
                      {filters.sort_by === 'performance' &&
                        (filters.sort_desc ? (
                          <SortDesc className="ml-1 h-4 w-4" />
                        ) : (
                          <SortAsc className="ml-1 h-4 w-4" />
                        ))}
                    </div>
                  </th>
                  <th
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                    onClick={() => handleSort('risk_score')}
                  >
                    <div className="flex items-center">
                      Risk
                      {filters.sort_by === 'risk_score' &&
                        (filters.sort_desc ? (
                          <SortDesc className="ml-1 h-4 w-4" />
                        ) : (
                          <SortAsc className="ml-1 h-4 w-4" />
                        ))}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    İlerleme
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Kayıtlar
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Son Aktivite
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    İşlemler
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {overview.summaries.map((summary) => (
                  <StudentReportRow
                    key={summary.student_id}
                    summary={summary}
                    isSelected={selectedStudents.includes(summary.student_id)}
                    onSelect={(selected) =>
                      handleSelectStudent(summary.student_id, selected)
                    }
                    onViewDetails={handleViewDetails}
                  />
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {overview.pagination.pages > 1 && (
            <div className="px-6 py-4 flex items-center justify-between border-t">
              <div className="text-sm text-gray-700">
                Toplam {overview.pagination.total} kayıttan{' '}
                {(filters.page! - 1) * filters.per_page! + 1} -{' '}
                {Math.min(
                  filters.page! * filters.per_page!,
                  overview.pagination.total
                )}{' '}
                arası gösteriliyor
              </div>

              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setFilters({ ...filters, page: filters.page! - 1 })
                  }
                  disabled={filters.page === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>

                <span className="text-sm">
                  Sayfa {filters.page} / {overview.pagination.pages}
                </span>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setFilters({ ...filters, page: filters.page! + 1 })
                  }
                  disabled={filters.page === overview.pagination.pages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </Card>
      ) : (
        <Card className="p-12">
          <div className="text-center">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Öğrenci bulunamadı.</p>
          </div>
        </Card>
      )}
    </div>
  );
}
