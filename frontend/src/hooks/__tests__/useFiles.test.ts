import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import * as React from 'react';
import { toast } from 'sonner';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { filesApi } from '@/api/files';

import {
  useFileUpload,
  useSingleFileUpload,
  useDeleteFile,
  useFileInfo,
  useFilesByEntity,
  useCourseMaterialUpload,
  useDownloadFile,
} from '../useFiles';

// Mock dependencies
vi.mock('@/api/files');
vi.mock('sonner');

const mockFilesApi = vi.mocked(filesApi);
const mockToast = vi.mocked(toast);

// Test wrapper with QueryClient
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => 
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

describe('useFiles hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useFileUpload', () => {
    it('uploads files successfully', async () => {
      const mockResponse = [
        {
          id: '1',
          filename: 'test1.txt',
          originalName: 'test1.txt',
          size: 100,
          mimetype: 'text/plain',
          url: 'http://example.com/test1.txt',
          uploadedAt: '2023-01-01T00:00:00Z',
        },
      ];

      mockFilesApi.uploadFiles.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useFileUpload(), {
        wrapper: createWrapper(),
      });

      const files = [new File(['test'], 'test1.txt', { type: 'text/plain' })];
      
      result.current.mutate({
        files,
        entityType: 'course_material',
        entityId: '123',
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mockFilesApi.uploadFiles).toHaveBeenCalledWith(
        files,
        'course_material',
        '123'
      );
      expect(mockToast.success).toHaveBeenCalledWith('1 file(s) uploaded successfully');
    });

    it('handles upload errors', async () => {
      const error = new Error('Upload failed');
      mockFilesApi.uploadFiles.mockRejectedValue(error);

      const { result } = renderHook(() => useFileUpload(), {
        wrapper: createWrapper(),
      });

      const files = [new File(['test'], 'test.txt', { type: 'text/plain' })];
      
      result.current.mutate({ files });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(mockToast.error).toHaveBeenCalledWith(
        'Failed to upload file(s). Please try again.'
      );
    });
  });

  describe('useSingleFileUpload', () => {
    it('uploads a single file successfully', async () => {
      const mockResponse = {
        id: '1',
        filename: 'test.txt',
        originalName: 'test.txt',
        size: 100,
        mimetype: 'text/plain',
        url: 'http://example.com/test.txt',
        uploadedAt: '2023-01-01T00:00:00Z',
      };

      mockFilesApi.uploadSingleFile.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useSingleFileUpload(), {
        wrapper: createWrapper(),
      });

      const file = new File(['test'], 'test.txt', { type: 'text/plain' });
      
      result.current.mutate({
        file,
        entityType: 'user_profile',
        entityId: 'avatar',
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mockFilesApi.uploadSingleFile).toHaveBeenCalledWith(
        file,
        'user_profile',
        'avatar'
      );
      expect(mockToast.success).toHaveBeenCalledWith('File uploaded successfully');
    });
  });

  describe('useDeleteFile', () => {
    it('deletes file successfully', async () => {
      mockFilesApi.deleteFile.mockResolvedValue(undefined);

      const { result } = renderHook(() => useDeleteFile(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('file-123');

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mockFilesApi.deleteFile).toHaveBeenCalledWith('file-123');
      expect(mockToast.success).toHaveBeenCalledWith('File deleted successfully');
    });

    it('handles delete errors', async () => {
      const error = new Error('Delete failed');
      mockFilesApi.deleteFile.mockRejectedValue(error);

      const { result } = renderHook(() => useDeleteFile(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('file-123');

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(mockToast.error).toHaveBeenCalledWith(
        'Failed to delete file. Please try again.'
      );
    });
  });

  describe('useFileInfo', () => {
    it('fetches file info successfully', async () => {
      const mockFileInfo = {
        id: '1',
        name: 'test.txt',
        size: 100,
        type: 'text/plain',
        url: 'http://example.com/test.txt',
        uploadedAt: '2023-01-01T00:00:00Z',
      };

      mockFilesApi.getFileInfo.mockResolvedValue(mockFileInfo);

      const { result } = renderHook(() => useFileInfo('file-123'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockFileInfo);
      expect(mockFilesApi.getFileInfo).toHaveBeenCalledWith('file-123');
    });

    it('does not fetch when fileId is empty', () => {
      const { result } = renderHook(() => useFileInfo(''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(mockFilesApi.getFileInfo).not.toHaveBeenCalled();
    });
  });

  describe('useFilesByEntity', () => {
    it('fetches files by entity successfully', async () => {
      const mockFiles = [
        {
          id: '1',
          name: 'test1.txt',
          size: 100,
          type: 'text/plain',
          url: 'http://example.com/test1.txt',
          uploadedAt: '2023-01-01T00:00:00Z',
        },
        {
          id: '2',
          name: 'test2.txt',
          size: 200,
          type: 'text/plain',
          url: 'http://example.com/test2.txt',
          uploadedAt: '2023-01-01T00:00:00Z',
        },
      ];

      mockFilesApi.getFilesByEntity.mockResolvedValue(mockFiles);

      const { result } = renderHook(
        () => useFilesByEntity('course_material', '123'),
        {
          wrapper: createWrapper(),
        }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockFiles);
      expect(mockFilesApi.getFilesByEntity).toHaveBeenCalledWith(
        'course_material',
        '123'
      );
    });

    it('does not fetch when parameters are empty', () => {
      const { result } = renderHook(() => useFilesByEntity('', ''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(mockFilesApi.getFilesByEntity).not.toHaveBeenCalled();
    });
  });

  describe('useCourseMaterialUpload', () => {
    it('uploads course material successfully', async () => {
      const mockResponse = {
        id: '1',
        filename: 'material.pdf',
        originalName: 'Course Material.pdf',
        size: 1024000,
        mimetype: 'application/pdf',
        url: 'http://example.com/material.pdf',
        uploadedAt: '2023-01-01T00:00:00Z',
      };

      mockFilesApi.uploadCourseMaterial.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useCourseMaterialUpload(), {
        wrapper: createWrapper(),
      });

      const file = new File(['content'], 'material.pdf', { type: 'application/pdf' });
      
      result.current.mutate({
        file,
        courseId: '456',
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mockFilesApi.uploadCourseMaterial).toHaveBeenCalledWith(file, '456');
      expect(mockToast.success).toHaveBeenCalledWith(
        'Course material uploaded successfully'
      );
    });
  });

  describe('useDownloadFile', () => {
    it('downloads file successfully', async () => {
      const mockBlob = new Blob(['file content'], { type: 'text/plain' });
      mockFilesApi.downloadFile.mockResolvedValue(mockBlob);

      // Mock URL.createObjectURL and related methods
      const mockUrl = 'blob:http://example.com/123';
      global.URL.createObjectURL = vi.fn(() => mockUrl);
      global.URL.revokeObjectURL = vi.fn();
      
      // Mock document methods
      const mockLink = document.createElement('a');
      mockLink.click = vi.fn();
      const mockCreateElement = vi.spyOn(document, 'createElement').mockReturnValue(mockLink);
      const mockAppendChild = vi.spyOn(document.body, 'appendChild').mockImplementation((node) => node);
      const mockRemoveChild = vi.spyOn(document.body, 'removeChild').mockImplementation((node) => node);

      const { result } = renderHook(() => useDownloadFile(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('file-123');

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mockFilesApi.downloadFile).toHaveBeenCalledWith('file-123');
      expect(global.URL.createObjectURL).toHaveBeenCalledWith(mockBlob);
      expect(mockCreateElement).toHaveBeenCalledWith('a');
      expect(mockLink.href).toBe(mockUrl);
      expect(mockLink.download).toBe('file-file-123');
      expect(mockLink.click).toHaveBeenCalled();
      expect(mockAppendChild).toHaveBeenCalledWith(mockLink);
      expect(mockRemoveChild).toHaveBeenCalledWith(mockLink);
      expect(global.URL.revokeObjectURL).toHaveBeenCalledWith(mockUrl);
      expect(mockToast.success).toHaveBeenCalledWith('File downloaded successfully');

      // Cleanup mocks
      mockCreateElement.mockRestore();
      mockAppendChild.mockRestore();
      mockRemoveChild.mockRestore();
    });

    it('handles download errors', async () => {
      const error = new Error('Download failed');
      mockFilesApi.downloadFile.mockRejectedValue(error);

      const { result } = renderHook(() => useDownloadFile(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('file-123');

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(mockToast.error).toHaveBeenCalledWith(
        'Failed to download file. Please try again.'
      );
    });
  });
});