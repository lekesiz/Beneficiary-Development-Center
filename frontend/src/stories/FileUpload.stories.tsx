import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';

import { FileUpload } from '@/components/ui/FileUpload';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  url?: string;
  progress?: number;
  error?: string;
}

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
    onUpload: {
      action: 'uploaded',
      description: 'Async function to handle file uploads',
    },
    onRemove: {
      action: 'removed',
      description: 'Callback when a file is removed',
    },
    maxFiles: {
      control: 'number',
      description: 'Maximum number of files allowed',
    },
    maxSize: {
      control: 'number',
      description: 'Maximum file size in bytes',
    },
    acceptedTypes: {
      control: 'array',
      description: 'Array of accepted MIME types',
    },
    multiple: {
      control: 'boolean',
      description: 'Allow multiple file uploads',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable the upload component',
    },
    showPreview: {
      control: 'boolean',
      description: 'Show file previews',
    },
  },
  args: {
    onUpload: async (files: File[]) => {
      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return files.map((file, index) => ({
        id: `file-${Date.now()}-${index}`,
        name: file.name,
        size: file.size,
        type: file.type,
        url: URL.createObjectURL(file),
      }));
    },
  },
} satisfies Meta<typeof FileUpload>;

export default meta;
type Story = StoryObj<typeof meta>;

// Helper component for demos with state management
const FileUploadDemo = (props: any) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async (files: File[]) => {
    setIsUploading(true);
    try {
      const result = await props.onUpload(files);
      setUploadedFiles([...uploadedFiles, ...result]);
      return result;
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemove = (fileId: string) => {
    setUploadedFiles(uploadedFiles.filter(f => f.id !== fileId));
    props.onRemove?.(fileId);
  };

  return (
    <div className="w-[500px]">
      <FileUpload
        {...props}
        onUpload={handleUpload}
        onRemove={handleRemove}
        uploadedFiles={uploadedFiles}
        disabled={props.disabled || isUploading}
      />
      {isUploading && (
        <p className="mt-2 text-sm text-gray-500">Uploading...</p>
      )}
    </div>
  );
};

export const Default: Story = {
  render: (args) => <FileUploadDemo {...args} />,
};

export const MultipleFiles: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    multiple: true,
    maxFiles: 5,
  },
};

export const SingleFile: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    multiple: false,
  },
};

export const WithSizeLimit: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    maxSize: 5 * 1024 * 1024, // 5MB
    multiple: true,
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
  },
};

export const WithInitialFiles: Story = {
  render: () => {
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([
      {
        id: 'file-1',
        name: 'document1.pdf',
        size: 1024 * 100,
        type: 'application/pdf',
      },
      {
        id: 'file-2',
        name: 'image1.jpg',
        size: 1024 * 200,
        type: 'image/jpeg',
      },
    ]);

    return (
      <div className="w-[500px]">
        <FileUpload
          onUpload={async (files) => {
            const newFiles = files.map((file, index) => ({
              id: `file-${Date.now()}-${index}`,
              name: file.name,
              size: file.size,
              type: file.type,
            }));
            setUploadedFiles([...uploadedFiles, ...newFiles]);
            return newFiles;
          }}
          onRemove={(fileId) => {
            setUploadedFiles(uploadedFiles.filter((f) => f.id !== fileId));
          }}
          uploadedFiles={uploadedFiles}
          multiple
        />
      </div>
    );
  },
};

export const VideoFiles: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    acceptedTypes: ['video/mp4', 'video/mpeg', 'video/quicktime'],
    maxSize: 100 * 1024 * 1024, // 100MB
  },
};

export const ImageFiles: Story = {
  render: (args) => <FileUploadDemo {...args} />,
  args: {
    acceptedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    showPreview: true,
  },
};

export const CustomStyling: Story = {
  args: {
    className: 'border-4 border-dashed border-purple-300 bg-purple-50',
    multiple: true,
  },
};

export const WithProgress: Story = {
  render: () => {
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

    const handleUpload = async (files: File[]) => {
      const newFiles = files.map((file, index) => ({
        id: `file-${Date.now()}-${index}`,
        name: file.name,
        size: file.size,
        type: file.type,
        progress: 0,
      }));

      setUploadedFiles(prev => [...prev, ...newFiles]);

      // Simulate upload progress
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 200));
        setUploadedFiles(prev =>
          prev.map(f =>
            newFiles.find(nf => nf.id === f.id)
              ? { ...f, progress: i }
              : f
          )
        );
      }

      return newFiles.map(f => ({ ...f, progress: 100 }));
    };

    return (
      <div className="w-[500px]">
        <FileUpload
          onUpload={handleUpload}
          onRemove={(fileId) => {
            setUploadedFiles(uploadedFiles.filter(f => f.id !== fileId));
          }}
          uploadedFiles={uploadedFiles}
          multiple
        />
      </div>
    );
  },
};

export const WithError: Story = {
  render: () => {
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([
      {
        id: 'file-1',
        name: 'failed-upload.pdf',
        size: 1024 * 100,
        type: 'application/pdf',
        error: 'Upload failed: Network error',
      },
    ]);

    return (
      <div className="w-[500px]">
        <FileUpload
          onUpload={async (files) => {
            // Simulate some files failing
            const newFiles = files.map((file, index) => ({
              id: `file-${Date.now()}-${index}`,
              name: file.name,
              size: file.size,
              type: file.type,
              error: index % 2 === 0 ? 'Upload failed' : undefined,
            }));
            setUploadedFiles([...uploadedFiles, ...newFiles]);
            return newFiles;
          }}
          onRemove={(fileId) => {
            setUploadedFiles(uploadedFiles.filter(f => f.id !== fileId));
          }}
          uploadedFiles={uploadedFiles}
          multiple
        />
      </div>
    );
  },
};