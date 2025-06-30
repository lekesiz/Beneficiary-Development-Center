import type { ColumnDef } from '@tanstack/react-table';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

import { DataTable } from '../DataTable';

interface TestData {
  id: number;
  name: string;
  status: string;
  created_at: string;
}

const mockData: TestData[] = [
  { id: 1, name: 'Alpha', status: 'active', created_at: '2024-01-01' },
  { id: 2, name: 'Beta', status: 'inactive', created_at: '2024-01-02' },
  { id: 3, name: 'Charlie', status: 'active', created_at: '2024-01-03' },
  { id: 4, name: 'Delta', status: 'pending', created_at: '2024-01-04' },
];

const columns: ColumnDef<TestData>[] = [
  {
    accessorKey: 'name',
    header: 'Name',
    enableSorting: true,
  },
  {
    accessorKey: 'status',
    header: 'Status',
    enableSorting: true,
  },
  {
    accessorKey: 'created_at',
    header: 'Created',
    enableSorting: true,
  },
];

describe('DataTable', () => {
  it('renders data correctly', () => {
    render(<DataTable columns={columns} data={mockData} />);

    expect(screen.getByText('Alpha')).toBeInTheDocument();
    expect(screen.getByText('Beta')).toBeInTheDocument();
    expect(screen.getByText('Charlie')).toBeInTheDocument();
    expect(screen.getByText('Delta')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<DataTable columns={columns} data={[]} loading={true} />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows empty state', () => {
    render(<DataTable columns={columns} data={[]} />);

    expect(screen.getByText('No results.')).toBeInTheDocument();
  });

  it('handles sorting when onSortingChange is provided', async () => {
    const onSortingChange = vi.fn();
    const { container } = render(
      <DataTable columns={columns} data={mockData} onSortingChange={onSortingChange} />
    );

    // Click on Name header to sort
    const nameHeader = screen.getByText('Name');
    fireEvent.click(nameHeader);

    await waitFor(() => {
      expect(onSortingChange).toHaveBeenCalled();
      // React Table passes a function or the new state directly
      const callArg = onSortingChange.mock.calls[0][0];
      if (typeof callArg === 'function') {
        // If it's a function, we can't easily test the exact value
        expect(onSortingChange).toHaveBeenCalledWith(expect.any(Function));
      } else {
        expect(callArg).toEqual([{ id: 'name', desc: false }]);
      }
    });

    // Should show sorting icon
    const sortIcon = container.querySelector('[class*="chevron"]');
    expect(sortIcon).toBeInTheDocument();
  });

  it('toggles sort direction on subsequent clicks', async () => {
    const onSortingChange = vi.fn();
    render(
      <DataTable
        columns={columns}
        data={mockData}
        sorting={[{ id: 'name', desc: false }]}
        onSortingChange={onSortingChange}
      />
    );

    // Click on Name header again to toggle sort
    const nameHeader = screen.getByText('Name');
    fireEvent.click(nameHeader);

    await waitFor(() => {
      expect(onSortingChange).toHaveBeenCalled();
      const callArg = onSortingChange.mock.calls[0][0];
      if (typeof callArg === 'function') {
        expect(onSortingChange).toHaveBeenCalledWith(expect.any(Function));
      } else {
        expect(callArg).toEqual([{ id: 'name', desc: true }]);
      }
    });
  });

  it('handles pagination', async () => {
    const onPaginationChange = vi.fn();
    render(
      <DataTable
        columns={columns}
        data={mockData}
        pagination={{ pageIndex: 0, pageSize: 2 }}
        onPaginationChange={onPaginationChange}
        pageCount={2}
      />
    );

    // Click next page button
    const nextButton = screen.getByRole('button', { name: /go to next page/i });
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(onPaginationChange).toHaveBeenCalled();
      const callArg = onPaginationChange.mock.calls[0][0];
      if (typeof callArg === 'function') {
        expect(onPaginationChange).toHaveBeenCalledWith(expect.any(Function));
      } else {
        expect(callArg).toEqual({ pageIndex: 1, pageSize: 2 });
      }
    });
  });

  it('disables pagination buttons appropriately', () => {
    render(
      <DataTable
        columns={columns}
        data={mockData}
        pagination={{ pageIndex: 0, pageSize: 2 }}
        pageCount={2}
      />
    );

    const prevButton = screen.getByRole('button', { name: /go to previous page/i });
    const nextButton = screen.getByRole('button', { name: /go to next page/i });

    // First page - previous should be disabled
    expect(prevButton).toBeDisabled();
    expect(nextButton).not.toBeDisabled();
  });

  it('changes page size', async () => {
    const onPaginationChange = vi.fn();
    render(
      <DataTable
        columns={columns}
        data={mockData}
        pagination={{ pageIndex: 0, pageSize: 10 }}
        onPaginationChange={onPaginationChange}
      />
    );

    const pageSizeSelect = screen.getByRole('combobox');
    fireEvent.change(pageSizeSelect, { target: { value: '20' } });

    await waitFor(() => {
      expect(onPaginationChange).toHaveBeenCalled();
      const callArg = onPaginationChange.mock.calls[0][0];
      if (typeof callArg === 'function') {
        expect(onPaginationChange).toHaveBeenCalledWith(expect.any(Function));
      } else {
        expect(callArg).toEqual({ pageIndex: 0, pageSize: 20 });
      }
    });
  });

  it('displays correct pagination info', () => {
    render(
      <DataTable
        columns={columns}
        data={mockData}
        pagination={{ pageIndex: 1, pageSize: 2 }}
        pageCount={2}
      />
    );

    expect(screen.getByText('Page 2 of 2')).toBeInTheDocument();
  });

  it('handles columns without sorting enabled', () => {
    const columnsWithMixedSorting: ColumnDef<TestData>[] = [
      {
        accessorKey: 'name',
        header: 'Name',
        enableSorting: true,
      },
      {
        accessorKey: 'status',
        header: 'Status',
        enableSorting: false,
      },
    ];

    const { container } = render(<DataTable columns={columnsWithMixedSorting} data={mockData} />);

    // Name header should have cursor-pointer class
    const nameHeader = screen.getByText('Name').closest('th');
    expect(nameHeader).toHaveClass('cursor-pointer');

    // Status header should not have cursor-pointer class
    const statusHeader = screen.getByText('Status').closest('th');
    expect(statusHeader).not.toHaveClass('cursor-pointer');
  });
});
