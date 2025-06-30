import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';

export interface DashboardStats {
  total_beneficiaries: number;
  active_programs: number;
  completed_evaluations: number;
  completion_rate: number;
  beneficiary_growth: string;
  program_growth: string;
  evaluation_growth: string;
  completion_growth: string;
}

export interface RecentActivity {
  id: number;
  title: string;
  description: string;
  time: string;
  type: 'beneficiary' | 'program' | 'evaluation' | 'coach_note';
  user_name?: string;
  created_at: string;
}

export interface UpcomingEvent {
  id: number;
  title: string;
  date: string;
  participants: number;
  type: 'course_session' | 'evaluation' | 'program_start';
  location?: string;
}

export interface DashboardData {
  statistics: DashboardStats;
  recent_activities: RecentActivity[];
  upcoming_events: UpcomingEvent[];
}

export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: async (): Promise<DashboardStats> => {
      const response = await apiClient.get('/dashboard/stats');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
};

export const useRecentActivities = () => {
  return useQuery({
    queryKey: ['dashboard', 'activities'],
    queryFn: async (): Promise<RecentActivity[]> => {
      const response = await apiClient.get('/dashboard/activities?limit=10');
      return response.data.activities;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 2 * 60 * 1000, // Refresh every 2 minutes
  });
};

export const useUpcomingEvents = () => {
  return useQuery({
    queryKey: ['dashboard', 'events'],
    queryFn: async (): Promise<UpcomingEvent[]> => {
      const response = await apiClient.get('/dashboard/upcoming-events?limit=5');
      return response.data.events;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 10 * 60 * 1000, // Refresh every 10 minutes
  });
};

export const useDashboardData = () => {
  const statsQuery = useDashboardStats();
  const activitiesQuery = useRecentActivities();
  const eventsQuery = useUpcomingEvents();

  return {
    stats: statsQuery.data,
    activities: activitiesQuery.data,
    events: eventsQuery.data,
    isLoading: statsQuery.isLoading || activitiesQuery.isLoading || eventsQuery.isLoading,
    isError: statsQuery.isError || activitiesQuery.isError || eventsQuery.isError,
    error: statsQuery.error || activitiesQuery.error || eventsQuery.error,
    refetch: () => {
      statsQuery.refetch();
      activitiesQuery.refetch();
      eventsQuery.refetch();
    }
  };
};