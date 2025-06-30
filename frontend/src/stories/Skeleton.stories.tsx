import type { Meta, StoryObj } from '@storybook/react';

import { Skeleton } from '@/components/ui/Skeleton';

const meta = {
  title: 'UI/Skeleton',
  component: Skeleton,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Skeleton screens provide a low fidelity representation of content before it loads to improve perceived performance.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    className: {
      control: 'text',
      description: 'Additional CSS classes to apply',
    },
  },
} satisfies Meta<typeof Skeleton>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    className: 'w-[200px] h-[20px]',
  },
};

export const Circle: Story = {
  args: {
    className: 'h-12 w-12 rounded-full',
  },
};

export const Square: Story = {
  args: {
    className: 'h-16 w-16 rounded-md',
  },
};

export const TextBlock: Story = {
  render: () => (
    <div className="space-y-2">
      <Skeleton className="h-4 w-[250px]" />
      <Skeleton className="h-4 w-[200px]" />
      <Skeleton className="h-4 w-[230px]" />
    </div>
  ),
};

export const Card: Story = {
  render: () => (
    <div className="w-[300px] rounded-lg border p-4">
      <div className="flex items-center space-x-4 mb-4">
        <Skeleton className="h-12 w-12 rounded-full" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-[150px]" />
          <Skeleton className="h-3 w-[100px]" />
        </div>
      </div>
      <div className="space-y-2">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-3/4" />
      </div>
    </div>
  ),
};

export const FormField: Story = {
  render: () => (
    <div className="w-[300px] space-y-2">
      <Skeleton className="h-4 w-[100px]" />
      <Skeleton className="h-10 w-full rounded-md" />
    </div>
  ),
};

export const ButtonGroup: Story = {
  render: () => (
    <div className="flex space-x-2">
      <Skeleton className="h-10 w-24 rounded-md" />
      <Skeleton className="h-10 w-32 rounded-md" />
      <Skeleton className="h-10 w-20 rounded-md" />
    </div>
  ),
};

export const List: Story = {
  render: () => (
    <div className="w-[400px] space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center space-x-4">
          <Skeleton className="h-10 w-10 rounded" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  ),
};
