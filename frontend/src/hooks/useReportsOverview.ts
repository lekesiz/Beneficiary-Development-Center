import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import apiClient from '@/api/client';

export interface StudentReportSummary {
  student_id: number;
  student_name: string;
  student_email: string;
  performance_index: number;
  risk_score: 'Low' | 'Medium' | 'High' | 'Unknown';
  risk_indicators: string[];
  progress_summary: string;
  completion_rate: number;
  average_score: number;
  active_learning_paths: number;
  recent_evaluations: number;
  enrollments: Array<{
    type: 'program' | 'course';
    id: number;
    name: string;
    progress: number;
  }>;
  last_activity: string | null;
  needs_attention: boolean;
}

export interface ReportsOverviewResponse {
  summaries: StudentReportSummary[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
  filters_applied: {
    risk: string | null;
    min_performance: number | null;
    max_performance: number | null;
    program_id: number | null;
    course_id: number | null;
    search: string | null;
  };
}

export interface ReportsOverviewFilters {
  page?: number;
  per_page?: number;
  risk?: 'Low' | 'Medium' | 'High';
  min_performance?: number;
  max_performance?: number;
  program_id?: number;
  course_id?: number;
  search?: string;
  sort_by?: 'risk_score' | 'performance' | 'name';
  sort_desc?: boolean;
}

export interface CoachNote {
  student_id: number;
  coach_id: number;
  coach_name: string;
  note: string;
  created_at: string;
}

export interface BatchExportRequest {
  student_ids: number[];
  format?: 'json' | 'pdf';
}

// API client functions
const reportsOverviewApi = {
  // Get reports overview
  getReportsOverview: async (
    filters?: ReportsOverviewFilters
  ): Promise<ReportsOverviewResponse> => {
    const params = new URLSearchParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }

    const response = await apiClient.get(
      `${API_BASE_URL}/reports/overview?${params}`
    );
    return response.data;
  },

  // Add coach note
  addCoachNote: async (
    studentId: number,
    note: string
  ): Promise<{ success: boolean; note: CoachNote }> => {
    const response = await apiClient.post(
      `${API_BASE_URL}/reports/students/${studentId}/note`,
      {
        note,
      }
    );
    return response.data;
  },

  // Export batch reports
  exportBatchReports: async ({
    student_ids,
    format = 'json',
  }: BatchExportRequest) => {
    const response = await apiClient.post(
      `${API_BASE_URL}/reports/export/batch`,
      { student_ids, format },
      { responseType: 'blob' }
    );

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute(
      'download',
      `student_reports_batch_${
        new Date().toISOString().split('T')[0]
      }.${format}`
    );
    document.body.appendChild(link);
    link.click();
    link.parentNode?.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};

// React Query hooks

// Get reports overview
export const useReportsOverview = (filters?: ReportsOverviewFilters) => {
  return useQuery({
    queryKey: ['reports-overview', filters],
    queryFn: () => reportsOverviewApi.getReportsOverview(filters),
    staleTime: 1000 * 60 * 2, // 2 minutes
    keepPreviousData: true, // Keep previous data while fetching new page
  });
};

// Add coach note
export const useAddCoachNote = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ studentId, note }: { studentId: number; note: string }) =>
      reportsOverviewApi.addCoachNote(studentId, note),
    onSuccess: (data) => {
      // Invalidate overview to refresh any cached data
      queryClient.invalidateQueries({ queryKey: ['reports-overview'] });
      // Also invalidate specific student report if it's cached
      queryClient.invalidateQueries({
        queryKey: ['development-report', data.note.student_id],
      });
    },
  });
};

// Export batch reports
export const useExportBatchReports = () => {
  return useMutation({
    mutationFn: reportsOverviewApi.exportBatchReports,
  });
};
