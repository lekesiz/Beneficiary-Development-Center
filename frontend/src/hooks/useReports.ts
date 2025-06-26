import { useQuery, useMutation } from '@tanstack/react-query';

import apiClient from '@/api/client';

export interface DevelopmentReport {
  student_name: string;
  progress_summary: string;
  ai_analysis: {
    learning_style: string;
    strengths: string[];
    weaknesses: string[];
    performance_risks: string[];
  };
  suggested_interventions: Array<{
    priority: 'high' | 'medium' | 'low';
    intervention: string;
    expected_outcome: string;
    timeline: string;
  }>;
  summary_score: {
    completion_rate: string;
    performance_index: number;
    risk_score: 'Low' | 'Medium' | 'High';
    overall_assessment: string;
  };
  recommendations: {
    immediate_actions: string[];
    long_term_goals: string[];
    support_needed: string[];
  };
  next_evaluation_focus: string[];
  visualization_data?: {
    performance_trend: Array<{
      date: string;
      score: number;
      index: number;
    }>;
    milestone_progress: Array<{
      path: string;
      progress: number;
    }>;
    skill_distribution: Array<{
      skill: string;
      focus_count: number;
      average_progress: number;
    }>;
  };
  metadata?: {
    generated_at: string;
    generated_by: string;
    report_period_days: number;
    tenant_id: number;
  };
}

export interface InsightsSummary {
  student_name: string;
  progress_summary: string;
  summary_score: DevelopmentReport['summary_score'];
  immediate_actions: string[];
  performance_trend: DevelopmentReport['visualization_data']['performance_trend'];
  generated_at: string;
}

// API client functions
const reportsApi = {
  // Get development report for a user
  getDevelopmentReport: async (
    userId: number,
    days: number = 30
  ): Promise<DevelopmentReport> => {
    const response = await apiClient.get(
      `${API_BASE_URL}/reports/development/${userId}`,
      {
        params: { days },
      }
    );
    return response.data;
  },

  // Get my development report
  getMyDevelopmentReport: async (
    days: number = 30
  ): Promise<DevelopmentReport> => {
    const response = await apiClient.get(
      `${API_BASE_URL}/reports/my-development`,
      {
        params: { days },
      }
    );
    return response.data;
  },

  // Get batch reports
  getBatchReports: async (userIds: number[], days: number = 30) => {
    const response = await apiClient.post(
      `${API_BASE_URL}/reports/development/batch`,
      {
        user_ids: userIds,
        days,
      }
    );
    return response.data;
  },

  // Get insights summary
  getInsightsSummary: async (): Promise<InsightsSummary> => {
    const response = await apiClient.get(
      `${API_BASE_URL}/reports/insights/summary`
    );
    return response.data;
  },

  // Download report
  downloadReport: async (
    userId: number,
    days: number = 30,
    format: 'json' = 'json'
  ) => {
    const response = await apiClient.get(
      `${API_BASE_URL}/reports/development/${userId}/download`,
      {
        params: { days, format },
        responseType: 'blob',
      }
    );

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute(
      'download',
      `development_report_${userId}_${
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

// Get development report for a user
export const useDevelopmentReport = (userId: number, days: number = 30) => {
  return useQuery({
    queryKey: ['development-report', userId, days],
    queryFn: () => reportsApi.getDevelopmentReport(userId, days),
    enabled: !!userId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Get my development report
export const useMyDevelopmentReport = (days: number = 30) => {
  return useQuery({
    queryKey: ['my-development-report', days],
    queryFn: () => reportsApi.getMyDevelopmentReport(days),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Get insights summary
export const useInsightsSummary = () => {
  return useQuery({
    queryKey: ['insights-summary'],
    queryFn: reportsApi.getInsightsSummary,
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};

// Generate batch reports
export const useGenerateBatchReports = () => {
  return useMutation({
    mutationFn: ({ userIds, days }: { userIds: number[]; days?: number }) =>
      reportsApi.getBatchReports(userIds, days || 30),
  });
};

// Download report
export const useDownloadReport = () => {
  return useMutation({
    mutationFn: ({
      userId,
      days,
      format,
    }: {
      userId: number;
      days?: number;
      format?: 'json';
    }) => reportsApi.downloadReport(userId, days || 30, format || 'json'),
  });
};
