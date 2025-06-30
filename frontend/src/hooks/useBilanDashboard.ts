import { useState, useCallback } from 'react';
import { bilanDashboardApi } from '../api/bilan';
import type { BilanDashboard } from '../types/bilan';

export const useBilanDashboard = () => {
  const [dashboard, setDashboard] = useState<BilanDashboard | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await bilanDashboardApi.getDashboard();
      setDashboard(response.data);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load dashboard');
      console.error('Error fetching Bilan dashboard:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    dashboard,
    loading,
    error,
    refetch: fetchDashboard
  };
};