import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import {
  mockBeneficiary,
  mockBeneficiaryList,
} from '@/tests/mocks/beneficiary';
import { server } from '@/tests/mocks/server';

import {
  useBeneficiaries,
  useBeneficiary,
  useCreateBeneficiary,
  useUpdateBeneficiary,
  useDeleteBeneficiary,
  useBeneficiaryStatistics,
} from '../useBeneficiaries';

const API_URL = 'http://localhost:5001/api/v1';

// Test wrapper
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useBeneficiaries hooks', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('useBeneficiaries', () => {
    it('fetches beneficiaries list successfully', async () => {
      const { result } = renderHook(() => useBeneficiaries(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data?.data.beneficiaries).toHaveLength(3);
      expect(result.current.data?.data.pagination.total).toBe(3);
    });

    it('handles query parameters correctly', async () => {
      const { result } = renderHook(
        () =>
          useBeneficiaries({
            page: 1,
            per_page: 10,
            search: 'john',
            status: 'active' as any,
          }),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Debug: log the actual response
      console.log('Test result:', result.current.data?.data);

      // Should filter by search and status
      expect(result.current.data?.data.beneficiaries).toHaveLength(1);
      expect(result.current.data?.data.beneficiaries[0].full_name).toBe(
        'John Doe'
      );
    });

    it('handles API errors', async () => {
      server.use(
        rest.get(`${API_URL}/beneficiaries`, (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ error: 'Server error' }));
        })
      );

      const { result } = renderHook(() => useBeneficiaries(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('useBeneficiary', () => {
    it('fetches single beneficiary successfully', async () => {
      const { result } = renderHook(() => useBeneficiary(1), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data?.data.beneficiary.id).toBe(1);
      expect(result.current.data?.data.beneficiary.full_name).toBe('John Doe');
    });

    it('skips fetch when enabled is false', () => {
      const { result } = renderHook(() => useBeneficiary(1, false), {
        wrapper: createWrapper(),
      });

      // When enabled is false, the query should not execute
      // Check if the query is in idle state and not fetching
      expect(result.current.isLoading).toBe(false);
      expect(result.current.data).toBeUndefined();
      expect(result.current.status).toBe('pending'); // Correct status for disabled query
    });

    it('handles 404 error', async () => {
      const { result } = renderHook(() => useBeneficiary(999), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('useCreateBeneficiary', () => {
    it('creates beneficiary successfully', async () => {
      const { result } = renderHook(() => useCreateBeneficiary(), {
        wrapper: createWrapper(),
      });

      const newData = {
        first_name: 'New',
        last_name: 'Beneficiary',
        email: 'new@example.com',
      };

      await result.current.mutateAsync(newData);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data?.data.message).toBe(
        'Beneficiary created successfully'
      );
      expect(result.current.data?.data.beneficiary.first_name).toBe('New');
    });

    it('handles validation errors', async () => {
      const { result } = renderHook(() => useCreateBeneficiary(), {
        wrapper: createWrapper(),
      });

      await expect(
        result.current.mutateAsync({ email: 'test@example.com' })
      ).rejects.toThrow();
    });
  });

  describe('useUpdateBeneficiary', () => {
    it('updates beneficiary successfully', async () => {
      const { result } = renderHook(() => useUpdateBeneficiary(), {
        wrapper: createWrapper(),
      });

      const updateData = {
        id: 1,
        data: { first_name: 'Updated' },
      };

      await result.current.mutateAsync(updateData);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data?.data.message).toBe(
        'Beneficiary updated successfully'
      );
    });

    it('handles 404 error', async () => {
      const { result } = renderHook(() => useUpdateBeneficiary(), {
        wrapper: createWrapper(),
      });

      await expect(
        result.current.mutateAsync({ id: 999, data: { first_name: 'Test' } })
      ).rejects.toThrow();
    });
  });

  describe('useDeleteBeneficiary', () => {
    it('deletes beneficiary successfully', async () => {
      const { result } = renderHook(() => useDeleteBeneficiary(), {
        wrapper: createWrapper(),
      });

      await result.current.mutateAsync(1);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data?.data.message).toBe(
        'Beneficiary deleted successfully'
      );
    });
  });

  describe('useBeneficiaryStatistics', () => {
    it('fetches statistics successfully', async () => {
      const { result } = renderHook(() => useBeneficiaryStatistics(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        console.log('Statistics query status:', {
          isSuccess: result.current.isSuccess,
          isError: result.current.isError,
          isLoading: result.current.isLoading,
          error: result.current.error,
          data: result.current.data
        });
        expect(result.current.isSuccess).toBe(true);
      }, { timeout: 3000 });

      expect(result.current.data?.data.statistics.total).toBe(3);
      expect(result.current.data?.data.statistics.by_status.active).toBe(1);
      expect(result.current.data?.data.statistics.by_employment.employed).toBe(
        2
      );
    });
  });
});
