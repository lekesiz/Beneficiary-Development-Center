import type { Meta, StoryObj } from '@storybook/react';
import { FileText, Users, BookOpen, Inbox, Search, AlertCircle } from 'lucide-react';

import { EmptyState } from './EmptyState';

const meta = {
  title: 'UI/EmptyState',
  component: EmptyState,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    icon: {
      control: false,
      description: 'Lucide React icon component to display',
    },
    title: {
      control: 'text',
      description: 'Main heading text',
    },
    description: {
      control: 'text',
      description: 'Descriptive text explaining the empty state',
    },
    action: {
      control: false,
      description: 'Optional action button configuration',
    },
  },
} satisfies Meta<typeof EmptyState>;

export default meta;
type Story = StoryObj<typeof meta>;

// Default story with all props
export const Default: Story = {
  args: {
    icon: FileText,
    title: 'No Documents Found',
    description: 'Upload your first document to get started. You can upload PDFs, Word documents, and more.',
    action: {
      text: 'Upload Document',
      onClick: () => console.log('Upload clicked'),
    },
  },
};

// Story without action button
export const WithoutAction: Story = {
  args: {
    icon: Inbox,
    title: 'Your Inbox is Empty',
    description: 'When you receive new messages or notifications, they will appear here.',
  },
};

// Story with Users icon
export const NoUsers: Story = {
  args: {
    icon: Users,
    title: 'No Team Members',
    description: 'Invite team members to collaborate on your projects and share insights.',
    action: {
      text: 'Invite Team Members',
      onClick: () => console.log('Invite clicked'),
    },
  },
};

// Story with BookOpen icon
export const NoCourses: Story = {
  args: {
    icon: BookOpen,
    title: 'No Courses Available',
    description: 'Create your first course to start delivering engaging learning experiences.',
    action: {
      text: 'Create Course',
      onClick: () => console.log('Create course clicked'),
    },
  },
};

// Story with Search icon for search results
export const NoSearchResults: Story = {
  args: {
    icon: Search,
    title: 'No Results Found',
    description: 'Try adjusting your search terms or filters to find what you\'re looking for.',
    action: {
      text: 'Clear Search',
      onClick: () => console.log('Clear search clicked'),
    },
  },
};

// Story with AlertCircle for error state
export const ErrorState: Story = {
  args: {
    icon: AlertCircle,
    title: 'Something Went Wrong',
    description: 'We encountered an error while loading this content. Please try again later.',
    action: {
      text: 'Try Again',
      onClick: () => console.log('Retry clicked'),
    },
  },
};

// Story with custom styling
export const CustomStyling: Story = {
  args: {
    icon: FileText,
    title: 'No Reports Generated',
    description: 'Generate your first report to gain insights into your data.',
    action: {
      text: 'Generate Report',
      onClick: () => console.log('Generate clicked'),
    },
    className: 'bg-blue-50 rounded-lg p-8',
  },
};

// Story with long description
export const LongDescription: Story = {
  args: {
    icon: BookOpen,
    title: 'Welcome to Your Library',
    description: 'Your personal library is empty right now. Start by adding books, articles, or documents that interest you. You can organize them into collections, add tags for easy searching, and even share them with others. Building your library helps you keep track of your learning journey and reference materials.',
    action: {
      text: 'Add Your First Item',
      onClick: () => console.log('Add item clicked'),
    },
  },
};