import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import apiClient from '@/api/client';

export interface StudentInfo {
  id: number;
  name: string;
  email: string;
  registration_date: string;
  last_login?: string;
  status: 'active' | 'inactive';
  profile_picture?: string;
  learning_style: string;
}

export interface DevelopmentScores {
  performance_index: number;
  engagement_score: number;
  completion_rate: number;
  average_score: number;
  passed_rate: number;
  risk_score: 'Low' | 'Medium' | 'High';
  risk_level: number;
  risk_factors: string[];
  total_evaluations: number;
  active_learning_paths: number;
  completed_learning_paths: number;
}

export interface RecentActivity {
  id: number;
  evaluation_id?: number;
  evaluation_title?: string;
  score?: number;
  passed?: boolean;
  completed_at?: string;
  duration_minutes?: number;
  attempt_number?: number;
  path_id?: number;
  path_title?: string;
  milestone_title?: string;
  progress?: number;
  status?: string;
  updated_at?: string;
  week_number?: number;
}

export interface Alert {
  type: 'warning' | 'danger';
  message: string;
  priority: 'high' | 'medium' | 'low';
}

export interface Intervention {
  type: 'immediate' | 'short_term' | 'long_term';
  title: string;
  description: string;
  expected_impact: string;
  priority: 'critical' | 'high' | 'medium';
  action_items: string[];
  timeline: string;
}

export interface AIAnalysis {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  learning_pattern: string;
  motivation_level: string;
  alerts?: Alert[];
  interventions?: Intervention[];
  intervention_suggestions?: string[]; // Legacy support
}

export interface VisualizationData {
  performance_trend: Array<{
    week: string;
    score: number | null;
    attempts: number;
  }>;
  milestone_completion: Array<{
    path_title: string;
    total_milestones: number;
    completed_milestones: number;
    progress: number;
  }>;
  skill_distribution: Array<{
    skill: string;
    total_focus: number;
    completed: number;
    in_progress: number;
    average_progress: number;
    mastery_level: string;
  }>;
}

export interface CoachNote {
  id: number;
  student_id: number;
  coach_id: number;
  note: string;
  category: string;
  created_at: string;
}

export interface NextRecommendations {
  next_evaluation?: {
    type: string;
    focus: string;
    suggested_date: string;
  };
  suggested_courses: any[];
  improvement_areas: string[];
  action_items: string[];
}

export interface StudentProfile {
  student_info: StudentInfo;
  development_scores: DevelopmentScores;
  recent_activities: {
    recent_evaluations: RecentActivity[];
    recent_sessions: RecentActivity[];
    last_activity_date?: string;
  };
  enrollments: {
    programs: any[];
    courses: any[];
    total_enrollments: number;
    active_enrollments: number;
  };
  ai_analysis: AIAnalysis;
  visualization_data: VisualizationData;
  coach_notes: CoachNote[];
  next_recommendations: NextRecommendations;
}

export interface ProfileRecommendations {
  next_evaluation?: {
    type: string;
    focus: string;
    suggested_date: string;
  };
  suggested_courses: any[];
  improvement_areas: string[];
  action_items: string[];
  ai_recommendations: string[];
  intervention_suggestions: string[];
}

// Fetch student profile
export function useStudentProfile(studentId: number | null) {
  return useQuery({
    queryKey: ['studentProfile', studentId],
    queryFn: async () => {
      if (!studentId) return null;
      const response = await apiClient.get(`/api/reports/profile/${studentId}`);
      return response.data as StudentProfile;
    },
    enabled: !!studentId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Add coach note
export function useAddCoachNote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      studentId,
      note,
      category = 'general',
    }: {
      studentId: number;
      note: string;
      category?: string;
    }) => {
      const response = await apiClient.post(
        `/api/reports/profile/${studentId}/notes`,
        {
          note,
          category,
        }
      );
      return response.data;
    },
    onSuccess: (data, variables) => {
      // Invalidate student profile to refresh notes
      queryClient.invalidateQueries({
        queryKey: ['studentProfile', variables.studentId],
      });
    },
  });
}

// Export student profile
export function useExportStudentProfile() {
  return useMutation({
    mutationFn: async ({
      studentId,
      format = 'json',
    }: {
      studentId: number;
      format?: 'json' | 'pdf';
    }) => {
      const response = await apiClient.get(
        `/api/reports/profile/${studentId}/export`,
        {
          params: { format },
          responseType: 'blob',
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `student_profile_${studentId}_${
          new Date().toISOString().split('T')[0]
        }.${format}`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return response.data;
    },
  });
}

// Get profile recommendations
export function useProfileRecommendations(studentId: number | null) {
  return useQuery({
    queryKey: ['profileRecommendations', studentId],
    queryFn: async () => {
      if (!studentId) return null;
      const response = await apiClient.get(
        `/api/reports/profile/${studentId}/recommendations`
      );
      return response.data as ProfileRecommendations;
    },
    enabled: !!studentId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
