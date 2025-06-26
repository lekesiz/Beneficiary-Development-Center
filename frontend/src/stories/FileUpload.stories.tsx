import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';

import { FileUpload } from '@/components/ui/FileUpload';

const meta = {
  title: 'UI/FileUpload',
  component: FileUpload,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A comprehensive file upload component with drag-and-drop, validation, and progress tracking.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    multiple: {
      control: 'boolean',
      description: 'Allow multiple file uploads',
    },
    accept: {
      control: 'text',
      description: 'Accepted file types (e.g., "image/*", ".pdf,.doc")',
    },
    maxSize: {
      control: 'number',
      description: 'Maximum file size in bytes',
    },
    onChange: {
      control: false,
      description: 'Callback when files change',
    },
    onRemove: {
      control: false,
      description: 'Callback when a file is removed',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable the upload component',
    },
    className: {
      control: 'text',
      description: 'Additional CSS classes',
    },
  },
} satisfies Meta<typeof FileUpload>;

export default meta;
type Story = StoryObj<typeof meta>;

// Helper component to demonstrate file handling
const FileUploadDemo = (args: any) => {
  const [files, setFiles] = useState<File[]>([]);

  return (
    <div className="w-[500px]">
      <FileUpload
        {...args}
        value={files}
        onChange={setFiles}
        onRemove={(index) => {
          setFiles(files.filter((_, i) => i !== index));
        }}
      />
      {files.length > 0 && (
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <h4 className="font-semibold mb-2">Selected Files:</h4>
          <ul className="space-y-1">
            {files.map((file, index) => (
              <li key={index} className="text-sm">
                {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export const Default: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {},
};

export const SingleFile: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    multiple: false,
  },
};

export const MultipleFiles: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    multiple: true,
  },
};

export const ImagesOnly: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    accept: 'image/*',
    multiple: true,
  },
};

export const DocumentsOnly: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    accept: '.pdf,.doc,.docx,.txt',
    multiple: true,
  },
};

export const SmallFileSize: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    maxSize: 1024 * 1024, // 1MB
    multiple: true,
  },
};

export const LargeFileSize: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true,
  },
};

export const Disabled: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    disabled: true,
  },
};

export const WithInitialFiles: Story = {
  render: () => {
    // Create mock files for demonstration
    const mockFiles = [
      new File(['Content 1'], 'document1.pdf', { type: 'application/pdf' }),
      new File(['Content 2'], 'image1.jpg', { type: 'image/jpeg' }),
    ];
    const [files, setFiles] = useState<File[]>(mockFiles);

    return (
      <div className="w-[500px]">
        <FileUpload
          value={files}
          onChange={setFiles}
          onRemove={(index) => {
            setFiles(files.filter((_, i) => i !== index));
          }}
          multiple
        />
      </div>
    );
  },
};

export const VideoFiles: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    accept: 'video/*',
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: false,
  },
};

export const SpreadsheetFiles: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    accept: '.xlsx,.xls,.csv',
    multiple: true,
  },
};

export const CustomStyling: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    className: 'border-blue-500 bg-blue-50',
    multiple: true,
  },
};