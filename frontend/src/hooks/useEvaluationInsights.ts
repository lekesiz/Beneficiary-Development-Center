/**
 * Custom hook for evaluation insights
 */
import { useQuery } from '@tanstack/react-query';

import { evaluationsApi, LearningInsights } from '@/api/evaluations';

/**
 * Hook to get AI-powered learning insights for an evaluation attempt
 */
export const useEvaluationInsights = (
  evaluationId: number,
  attemptId: number,
  options?: {
    enabled?: boolean;
    refetchOnWindowFocus?: boolean;
    staleTime?: number;
  }
) => {
  return useQuery<LearningInsights, Error>({
    queryKey: ['evaluationInsights', evaluationId, attemptId],
    queryFn: () =>
      evaluationsApi.adaptive.getLearningInsights(evaluationId, attemptId),
    enabled: options?.enabled !== false && !!evaluationId && !!attemptId,
    staleTime: options?.staleTime || 10 * 60 * 1000, // 10 minutes by default
    refetchOnWindowFocus: options?.refetchOnWindowFocus !== false,
    retry: 2, // Retry twice on failure
  });
};

// Helper functions for insights visualization
export const getPerformanceLevelColor = (level: string): string => {
  const colors = {
    expert: 'text-green-700 bg-green-100',
    proficient: 'text-blue-700 bg-blue-100',
    developing: 'text-yellow-700 bg-yellow-100',
    novice: 'text-orange-700 bg-orange-100',
    beginner: 'text-red-700 bg-red-100',
  };
  return colors[level as keyof typeof colors] || 'text-gray-700 bg-gray-100';
};

export const getPerformanceLevelLabel = (level: string): string => {
  const labels = {
    expert: 'Uzman',
    proficient: 'Yetkin',
    developing: 'Gelişmekte',
    novice: 'Acemi',
    beginner: 'Başlangıç',
  };
  return labels[level as keyof typeof labels] || level;
};

export const getTrendIcon = (
  trend: 'improving' | 'declining' | 'stable'
): string => {
  const icons = {
    improving: '📈',
    declining: '📉',
    stable: '➡️',
  };
  return icons[trend] || '➡️';
};

export const getTrendLabel = (
  trend: 'improving' | 'declining' | 'stable'
): string => {
  const labels = {
    improving: 'Gelişiyor',
    declining: 'Düşüşte',
    stable: 'Stabil',
  };
  return labels[trend] || 'Stabil';
};

export const getMetricColor = (value: number): string => {
  if (value >= 80) return 'text-green-600';
  if (value >= 60) return 'text-yellow-600';
  return 'text-red-600';
};

// Format performance metrics for display
export const formatPerformanceMetrics = (
  metrics: LearningInsights['performance_metrics']
) => {
  return {
    overallScore: {
      value: metrics.overall_score,
      label: 'Toplam Skor',
      formatted: metrics.overall_score.toFixed(1),
      color: getMetricColor(metrics.overall_score),
    },
    accuracy: {
      value: metrics.accuracy_percentage,
      label: 'Doğruluk Oranı',
      formatted: `${metrics.accuracy_percentage.toFixed(1)}%`,
      color: getMetricColor(metrics.accuracy_percentage),
    },
    timeEfficiency: {
      value: metrics.time_efficiency,
      label: 'Zaman Verimliliği',
      formatted: `${metrics.time_efficiency.toFixed(0)}%`,
      color: getMetricColor(metrics.time_efficiency),
    },
    consistency: {
      value: metrics.consistency_score,
      label: 'Tutarlılık',
      formatted: `${metrics.consistency_score.toFixed(0)}%`,
      color: getMetricColor(metrics.consistency_score),
    },
  };
};
