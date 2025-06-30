import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';

// Type definitions for analytics data
export interface PerformanceTrend {
  date: string;
  completions: number;
  active_users: number;
  average_score: number;
}

export interface PerformanceTrendsResponse {
  trends: PerformanceTrend[];
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  summary: {
    total_completions: number;
    unique_users: number;
    overall_average: number;
  };
}

export interface CompletionRate {
  program_id: number;
  program_name: string;
  total_enrolled: number;
  completed: number;
  in_progress: number;
  dropped: number;
  completion_rate: number;
  retention_rate: number;
}

export interface CompletionRatesResponse {
  programs: CompletionRate[];
  overall_stats: {
    total_enrolled: number;
    total_completed: number;
    total_in_progress: number;
    overall_completion_rate: number;
    overall_retention_rate: number;
  };
}

export interface EngagementMetric {
  user_id: number;
  user_name: string;
  email: string;
  recent_milestones: number;
  recent_evaluations: number;
  engagement_score: number;
  engagement_level: 'High' | 'Medium' | 'Low';
  last_activity: string | null;
}

export interface EngagementMetricsResponse {
  engagement_data: EngagementMetric[];
  summary: {
    total_users: number;
    high_engagement: number;
    medium_engagement: number;
    low_engagement: number;
    average_score: number;
    period_days: number;
  };
}

export interface RiskAnalysis {
  student_id: number;
  student_name: string;
  email: string;
  risk_score: number;
  risk_level: 'High' | 'Medium' | 'Low';
  risk_factors: string[];
  completion_rate: number;
  active_programs: number;
  last_activity: string | null;
}

export interface RiskAnalysisResponse {
  risk_analysis: RiskAnalysis[];
  summary: {
    total_students: number;
    high_risk: number;
    medium_risk: number;
    low_risk: number;
    needs_immediate_attention: number;
  };
}

export interface LearningPatterns {
  completion_by_hour: Array<{ hour: number; completions: number }>;
  completion_by_day: Array<{ day: string; day_number: number; completions: number }>;
  skill_preferences: Array<{ skill: string; completions: number }>;
  insights: {
    peak_learning_hour: string;
    peak_learning_day: string;
    average_completion_time_hours: number;
    total_completions_analyzed: number;
    analysis_period_days: number;
  };
}

// React Query hooks for analytics endpoints

export const usePerformanceTrends = (days: number = 30, userIds?: number[], programIds?: number[]) => {
  return useQuery({
    queryKey: ['analytics', 'performance-trends', days, userIds, programIds],
    queryFn: async (): Promise<PerformanceTrendsResponse> => {
      const params = new URLSearchParams();
      params.append('days', days.toString());
      
      if (userIds && userIds.length > 0) {
        userIds.forEach(id => params.append('user_ids', id.toString()));
      }
      
      if (programIds && programIds.length > 0) {
        programIds.forEach(id => params.append('program_ids', id.toString()));
      }

      const response = await apiClient.get(`/analytics/performance-trends?${params}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
};

export const useCompletionRates = () => {
  return useQuery({
    queryKey: ['analytics', 'completion-rates'],
    queryFn: async (): Promise<CompletionRatesResponse> => {
      const response = await apiClient.get('/analytics/completion-rates');
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 10 * 60 * 1000, // Refresh every 10 minutes
  });
};

export const useEngagementMetrics = (days: number = 30) => {
  return useQuery({
    queryKey: ['analytics', 'engagement-metrics', days],
    queryFn: async (): Promise<EngagementMetricsResponse> => {
      const response = await apiClient.get(`/analytics/engagement-metrics?days=${days}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
};

export const useRiskAnalysis = () => {
  return useQuery({
    queryKey: ['analytics', 'risk-analysis'],
    queryFn: async (): Promise<RiskAnalysisResponse> => {
      const response = await apiClient.get('/analytics/risk-analysis');
      return response.data;
    },
    staleTime: 15 * 60 * 1000, // 15 minutes
    refetchInterval: 15 * 60 * 1000, // Refresh every 15 minutes
  });
};

export const useLearningPatterns = (days: number = 60) => {
  return useQuery({
    queryKey: ['analytics', 'learning-patterns', days],
    queryFn: async (): Promise<LearningPatterns> => {
      const response = await apiClient.get(`/analytics/learning-patterns?days=${days}`);
      return response.data;
    },
    staleTime: 30 * 60 * 1000, // 30 minutes
    refetchInterval: 30 * 60 * 1000, // Refresh every 30 minutes
  });
};

// Combined analytics hook for dashboard use
export const useAnalyticsDashboard = (days: number = 30) => {
  const performanceTrends = usePerformanceTrends(days);
  const completionRates = useCompletionRates();
  const engagementMetrics = useEngagementMetrics(days);
  const riskAnalysis = useRiskAnalysis();

  return {
    performanceTrends: performanceTrends.data,
    completionRates: completionRates.data,
    engagementMetrics: engagementMetrics.data,
    riskAnalysis: riskAnalysis.data,
    isLoading: performanceTrends.isLoading || completionRates.isLoading || 
               engagementMetrics.isLoading || riskAnalysis.isLoading,
    isError: performanceTrends.isError || completionRates.isError || 
             engagementMetrics.isError || riskAnalysis.isError,
    error: performanceTrends.error || completionRates.error || 
           engagementMetrics.error || riskAnalysis.error,
    refetch: () => {
      performanceTrends.refetch();
      completionRates.refetch();
      engagementMetrics.refetch();
      riskAnalysis.refetch();
    }
  };
};