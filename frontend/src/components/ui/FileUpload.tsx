import { Upload, X, FileText, Image, Video, Music, Archive } from 'lucide-react';
import * as React from 'react';
import { useCallback, useState } from 'react';

import { cn } from '@/lib/utils';

import { Button } from './Button';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  url?: string;
  progress?: number;
  error?: string;
}

interface FileUploadProps {
  onUpload: (files: File[]) => Promise<UploadedFile[]>;
  onRemove?: (fileId: string) => void;
  maxFiles?: number;
  maxSize?: number; // in bytes
  acceptedTypes?: string[];
  multiple?: boolean;
  disabled?: boolean;
  className?: string;
  uploadedFiles?: UploadedFile[];
  showPreview?: boolean;
}

const getFileIcon = (type: string) => {
  if (type.startsWith('image/')) return <Image className="h-5 w-5" />;
  if (type.startsWith('video/')) return <Video className="h-5 w-5" />;
  if (type.startsWith('audio/')) return <Music className="h-5 w-5" />;
  if (type.includes('zip') || type.includes('rar') || type.includes('tar')) {
    return <Archive className="h-5 w-5" />;
  }
  return <FileText className="h-5 w-5" />;
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const FileUpload: React.FC<FileUploadProps> = ({
  onUpload,
  onRemove,
  maxFiles = 5,
  maxSize = 10 * 1024 * 1024, // 10MB
  acceptedTypes = ['*/*'],
  multiple = true,
  disabled = false,
  className,
  uploadedFiles = [],
  showPreview = true,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  const validateFile = (file: File): string | null => {
    if (maxSize && file.size > maxSize) {
      return `File size exceeds ${formatFileSize(maxSize)}`;
    }

    if (acceptedTypes.length > 0 && !acceptedTypes.includes('*/*')) {
      const isAccepted = acceptedTypes.some(type => {
        if (type.endsWith('/*')) {
          return file.type.startsWith(type.slice(0, -1));
        }
        return file.type === type;
      });

      if (!isAccepted) {
        return `File type ${file.type} is not accepted`;
      }
    }

    return null;
  };

  const handleFiles = useCallback(async (files: FileList) => {
    const fileArray = Array.from(files);
    const newErrors: string[] = [];

    // Check file limit
    if (uploadedFiles.length + fileArray.length > maxFiles) {
      newErrors.push(`Maximum ${maxFiles} files allowed`);
    }

    // Validate each file
    const validFiles: File[] = [];
    fileArray.forEach(file => {
      const error = validateFile(file);
      if (error) {
        newErrors.push(`${file.name}: ${error}`);
      } else {
        validFiles.push(file);
      }
    });

    setErrors(newErrors);

    if (validFiles.length > 0) {
      setUploading(true);
      try {
        await onUpload(validFiles);
      } catch (error) {
        setErrors(prev => [...prev, 'Upload failed. Please try again.']);
      } finally {
        setUploading(false);
      }
    }
  }, [uploadedFiles.length, maxFiles, onUpload]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (disabled || uploading) return;
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFiles(files);
    }
  }, [disabled, uploading, handleFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled && !uploading) {
      setIsDragOver(true);
    }
  }, [disabled, uploading]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFiles(files);
    }
    // Reset the input value so the same file can be selected again
    e.target.value = '';
  }, [handleFiles]);

  const canUpload = !disabled && !uploading && uploadedFiles.length < maxFiles;

  return (
    <div className={cn('w-full', className)}>
      {/* Upload Area */}
      <div
        className={cn(
          'border-2 border-dashed rounded-lg p-6 transition-colors',
          isDragOver
            ? 'border-primary bg-primary/5'
            : 'border-gray-300 hover:border-gray-400',
          disabled && 'opacity-50 cursor-not-allowed',
          !canUpload && 'bg-gray-50'
        )}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="text-center">
          <Upload
            className={cn(
              'mx-auto h-12 w-12 mb-4',
              canUpload ? 'text-gray-400' : 'text-gray-300'
            )}
          />
          
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-1">
              {canUpload
                ? 'Drag and drop files here, or click to select'
                : `Maximum ${maxFiles} files reached`}
            </p>
            {acceptedTypes.length > 0 && acceptedTypes[0] !== '*/*' && (
              <p className="text-xs text-gray-500">
                Accepted: {acceptedTypes.join(', ')}
              </p>
            )}
            <p className="text-xs text-gray-500">
              Max size: {formatFileSize(maxSize)}
            </p>
          </div>

          {canUpload && (
            <div>
              <Button
                variant="outline"
                disabled={disabled || uploading}
                loading={uploading}
                className="relative"
              >
                <Upload className="h-4 w-4 mr-2" />
                {uploading ? 'Uploading...' : 'Select Files'}
                <input
                  type="file"
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  multiple={multiple}
                  accept={acceptedTypes.join(',')}
                  onChange={handleFileSelect}
                  disabled={disabled || uploading}
                />
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="text-sm text-red-700">
            {errors.map((error, index) => (
              <div key={index}>{error}</div>
            ))}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setErrors([])}
            className="mt-2 text-red-600 hover:text-red-800"
          >
            Dismiss
          </Button>
        </div>
      )}

      {/* File Preview */}
      {showPreview && uploadedFiles.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            Uploaded Files ({uploadedFiles.length})
          </h4>
          <div className="space-y-2">
            {uploadedFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
              >
                <div className="flex items-center space-x-3">
                  <div className="text-gray-500">
                    {getFileIcon(file.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {file.progress !== undefined && file.progress < 100 && (
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                  )}

                  {file.error && (
                    <span className="text-xs text-red-600">{file.error}</span>
                  )}

                  {file.url && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => window.open(file.url, '_blank')}
                      className="text-xs"
                    >
                      View
                    </Button>
                  )}

                  {onRemove && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onRemove(file.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};