import { useQuery } from '@tanstack/react-query';

import { api } from '@/lib/api';

export interface DashboardStats {
  overall_progress: number;
  completed_milestones: number;
  weekly_hours: number;
  active_paths: number;
}

export interface UpcomingEvaluation {
  id: number;
  title: string;
  type: string;
  due_date: string;
}

export interface RecentAchievement {
  id: number;
  title: string;
  earned_at: string;
}

export interface DashboardAlert {
  type: 'warning' | 'info';
  message: string;
}

export interface StudentDashboard {
  stats: DashboardStats;
  upcoming_evaluations: UpcomingEvaluation[];
  recent_achievements: RecentAchievement[];
  alerts: DashboardAlert[];
}

export function useStudentDashboard() {
  return useQuery({
    queryKey: ['studentDashboard'],
    queryFn: async () => {
      const response = await api.get('/api/dashboard/student');
      return response.data as StudentDashboard;
    },
  });
}
