import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { filesApi, type UploadResponse, type FileInfo } from '@/api/files';

// Upload hooks
export const useFileUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      files,
      entityType,
      entityId,
    }: {
      files: File[];
      entityType?: string;
      entityId?: string;
    }) => {
      return filesApi.uploadFiles(files, entityType, entityId);
    },
    onSuccess: (data, variables) => {
      toast.success(`${data.length} file(s) uploaded successfully`);
      
      // Invalidate relevant queries
      if (variables.entityType && variables.entityId) {
        queryClient.invalidateQueries({
          queryKey: ['files', variables.entityType, variables.entityId],
        });
      }
      queryClient.invalidateQueries({ queryKey: ['files'] });
    },
    onError: (error) => {
      console.error('File upload failed:', error);
      toast.error('Failed to upload file(s). Please try again.');
    },
  });
};

export const useSingleFileUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      file,
      entityType,
      entityId,
    }: {
      file: File;
      entityType?: string;
      entityId?: string;
    }) => {
      return filesApi.uploadSingleFile(file, entityType, entityId);
    },
    onSuccess: (data, variables) => {
      toast.success('File uploaded successfully');
      
      // Invalidate relevant queries
      if (variables.entityType && variables.entityId) {
        queryClient.invalidateQueries({
          queryKey: ['files', variables.entityType, variables.entityId],
        });
      }
      queryClient.invalidateQueries({ queryKey: ['files'] });
    },
    onError: (error) => {
      console.error('File upload failed:', error);
      toast.error('Failed to upload file. Please try again.');
    },
  });
};

// Delete hook
export const useDeleteFile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (fileId: string) => filesApi.deleteFile(fileId),
    onSuccess: () => {
      toast.success('File deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['files'] });
    },
    onError: (error) => {
      console.error('File deletion failed:', error);
      toast.error('Failed to delete file. Please try again.');
    },
  });
};

// Query hooks
export const useFileInfo = (fileId: string) => {
  return useQuery({
    queryKey: ['files', fileId],
    queryFn: () => filesApi.getFileInfo(fileId),
    enabled: !!fileId,
  });
};

export const useFilesByEntity = (entityType: string, entityId: string) => {
  return useQuery({
    queryKey: ['files', entityType, entityId],
    queryFn: () => filesApi.getFilesByEntity(entityType, entityId),
    enabled: !!entityType && !!entityId,
  });
};

// Specialized upload hooks
export const useProfilePictureUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => filesApi.uploadProfilePicture(file),
    onSuccess: () => {
      toast.success('Profile picture updated successfully');
      queryClient.invalidateQueries({ queryKey: ['files', 'user_profile'] });
      queryClient.invalidateQueries({ queryKey: ['auth', 'me'] });
    },
    onError: (error) => {
      console.error('Profile picture upload failed:', error);
      toast.error('Failed to update profile picture. Please try again.');
    },
  });
};

export const useCourseMaterialUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, courseId }: { file: File; courseId: string }) =>
      filesApi.uploadCourseMaterial(file, courseId),
    onSuccess: (data, variables) => {
      toast.success('Course material uploaded successfully');
      queryClient.invalidateQueries({
        queryKey: ['files', 'course_material', variables.courseId],
      });
      queryClient.invalidateQueries({
        queryKey: ['courses', variables.courseId],
      });
    },
    onError: (error) => {
      console.error('Course material upload failed:', error);
      toast.error('Failed to upload course material. Please try again.');
    },
  });
};

export const useCourseMediaUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ files, courseId }: { files: File[]; courseId: string }) =>
      filesApi.uploadCourseMedia(files, courseId),
    onSuccess: (data, variables) => {
      toast.success(`${data.length} media file(s) uploaded successfully`);
      queryClient.invalidateQueries({
        queryKey: ['files', 'course_media', variables.courseId],
      });
      queryClient.invalidateQueries({
        queryKey: ['courses', variables.courseId],
      });
    },
    onError: (error) => {
      console.error('Course media upload failed:', error);
      toast.error('Failed to upload course media. Please try again.');
    },
  });
};

export const useProgramDocumentUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, programId }: { file: File; programId: string }) =>
      filesApi.uploadProgramDocument(file, programId),
    onSuccess: (data, variables) => {
      toast.success('Program document uploaded successfully');
      queryClient.invalidateQueries({
        queryKey: ['files', 'program_document', variables.programId],
      });
      queryClient.invalidateQueries({
        queryKey: ['programs', variables.programId],
      });
    },
    onError: (error) => {
      console.error('Program document upload failed:', error);
      toast.error('Failed to upload program document. Please try again.');
    },
  });
};

export const useBeneficiaryDocumentUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, beneficiaryId }: { file: File; beneficiaryId: string }) =>
      filesApi.uploadBeneficiaryDocument(file, beneficiaryId),
    onSuccess: (data, variables) => {
      toast.success('Beneficiary document uploaded successfully');
      queryClient.invalidateQueries({
        queryKey: ['files', 'beneficiary_document', variables.beneficiaryId],
      });
      queryClient.invalidateQueries({
        queryKey: ['beneficiaries', variables.beneficiaryId],
      });
    },
    onError: (error) => {
      console.error('Beneficiary document upload failed:', error);
      toast.error('Failed to upload beneficiary document. Please try again.');
    },
  });
};

// Download hook
export const useDownloadFile = () => {
  return useMutation({
    mutationFn: async (fileId: string) => {
      const blob = await filesApi.downloadFile(fileId);
      return { blob, fileId };
    },
    onSuccess: ({ blob, fileId }) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `file-${fileId}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('File downloaded successfully');
    },
    onError: (error) => {
      console.error('File download failed:', error);
      toast.error('Failed to download file. Please try again.');
    },
  });
};