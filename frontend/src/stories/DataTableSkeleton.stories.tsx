import type { Meta, StoryObj } from '@storybook/react';

import { DataTableSkeleton } from '@/components/common/DataTableSkeleton';

const meta = {
  title: 'Components/DataTableSkeleton',
  component: DataTableSkeleton,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'A skeleton loader that mimics the structure of a data table, providing visual feedback while data is loading.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    columns: {
      control: { type: 'number', min: 1, max: 10 },
      description: 'Number of columns to display',
    },
    rows: {
      control: { type: 'number', min: 1, max: 20 },
      description: 'Number of rows to display',
    },
    showPagination: {
      control: 'boolean',
      description: 'Whether to show pagination skeleton',
    },
    className: {
      control: 'text',
      description: 'Additional CSS classes',
    },
  },
} satisfies Meta<typeof DataTableSkeleton>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    columns: 5,
    rows: 10,
    showPagination: true,
  },
};

export const FewColumns: Story = {
  args: {
    columns: 3,
    rows: 8,
    showPagination: true,
  },
};

export const ManyColumns: Story = {
  args: {
    columns: 8,
    rows: 10,
    showPagination: true,
  },
};

export const FewRows: Story = {
  args: {
    columns: 5,
    rows: 3,
    showPagination: false,
  },
};

export const NoPagination: Story = {
  args: {
    columns: 5,
    rows: 10,
    showPagination: false,
  },
};

export const CompactTable: Story = {
  args: {
    columns: 4,
    rows: 5,
    showPagination: false,
  },
};

export const LargeTable: Story = {
  args: {
    columns: 10,
    rows: 20,
    showPagination: true,
  },
};

export const UserTable: Story = {
  name: 'User Table Example',
  args: {
    columns: 6,
    rows: 10,
    showPagination: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Example configuration for a typical user management table with columns for name, email, role, status, created date, and actions.',
      },
    },
  },
};

export const ProductTable: Story = {
  name: 'Product Table Example',
  args: {
    columns: 7,
    rows: 12,
    showPagination: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Example configuration for a product listing table with columns for image, name, category, price, stock, status, and actions.',
      },
    },
  },
};
