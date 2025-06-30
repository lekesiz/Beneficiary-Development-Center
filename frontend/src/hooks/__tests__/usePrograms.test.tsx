import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { programsApi } from '../../api/programs';
import type { ProgramFilters } from '../../types/program';
import { usePrograms } from '../usePrograms';

// Mock the API
vi.mock('../../api/programs', () => ({
  programsApi: {
    getAll: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('usePrograms', () => {
  const mockPrograms = {
    programs: [
      {
        id: 1,
        title: 'Program A',
        status: 'active',
        created_at: '2024-01-01',
      },
      {
        id: 2,
        title: 'Program B',
        status: 'draft',
        created_at: '2024-01-02',
      },
    ],
    pagination: {
      page: 1,
      per_page: 20,
      total: 2,
      pages: 1,
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches programs without filters', async () => {
    vi.mocked(programsApi.getAll).mockResolvedValue(mockPrograms);

    const { result } = renderHook(() => usePrograms(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(programsApi.getAll).toHaveBeenCalledWith(undefined);
    expect(result.current.data).toEqual(mockPrograms);
  });

  it('fetches programs with filters', async () => {
    const filters: ProgramFilters = {
      page: 2,
      per_page: 10,
      status: 'active',
      search: 'test',
    };

    vi.mocked(programsApi.getAll).mockResolvedValue(mockPrograms);

    const { result } = renderHook(() => usePrograms(filters), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(programsApi.getAll).toHaveBeenCalledWith(filters);
  });

  it('fetches programs with sorting parameters', async () => {
    const filters: ProgramFilters = {
      page: 1,
      per_page: 20,
      sort_by: 'title',
      sort_order: 'asc',
    };

    vi.mocked(programsApi.getAll).mockResolvedValue(mockPrograms);

    const { result } = renderHook(() => usePrograms(filters), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(programsApi.getAll).toHaveBeenCalledWith(filters);
  });

  it('refetches when filters change', async () => {
    const initialFilters: ProgramFilters = {
      page: 1,
      per_page: 20,
    };

    const updatedFilters: ProgramFilters = {
      page: 1,
      per_page: 20,
      sort_by: 'created_at',
      sort_order: 'desc',
    };

    vi.mocked(programsApi.getAll).mockResolvedValue(mockPrograms);

    const { result, rerender } = renderHook(({ filters }) => usePrograms(filters), {
      wrapper: createWrapper(),
      initialProps: { filters: initialFilters },
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(programsApi.getAll).toHaveBeenCalledTimes(1);
    expect(programsApi.getAll).toHaveBeenCalledWith(initialFilters);

    // Update filters
    rerender({ filters: updatedFilters });

    await waitFor(() => {
      expect(programsApi.getAll).toHaveBeenCalledTimes(2);
    });

    expect(programsApi.getAll).toHaveBeenLastCalledWith(updatedFilters);
  });

  it('handles different sort fields', async () => {
    const sortFields = ['title', 'created_at', 'start_date', 'status'];

    for (const sortField of sortFields) {
      const filters: ProgramFilters = {
        sort_by: sortField,
        sort_order: 'desc',
      };

      vi.mocked(programsApi.getAll).mockResolvedValue(mockPrograms);

      const { result } = renderHook(() => usePrograms(filters), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(programsApi.getAll).toHaveBeenCalledWith(filters);
    }
  });

  it('handles API errors', async () => {
    const error = new Error('API Error');
    vi.mocked(programsApi.getAll).mockRejectedValue(error);

    const { result } = renderHook(() => usePrograms(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBe(error);
  });

  it('respects stale time configuration', async () => {
    vi.mocked(programsApi.getAll).mockResolvedValue(mockPrograms);

    const { result } = renderHook(() => usePrograms(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Should only be called once within stale time
    expect(programsApi.getAll).toHaveBeenCalledTimes(1);
  });
});
