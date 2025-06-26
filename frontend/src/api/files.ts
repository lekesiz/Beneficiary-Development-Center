import apiClient from './client';

export interface UploadResponse {
  id: string;
  filename: string;
  originalName: string;
  size: number;
  mimetype: string;
  url: string;
  uploadedAt: string;
}

export interface FileInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  uploadedAt: string;
}

class FilesApi {
  async uploadFiles(files: File[], entityType?: string, entityId?: string): Promise<UploadResponse[]> {
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append('files', file);
    });

    if (entityType) {
      formData.append('entityType', entityType);
    }

    if (entityId) {
      formData.append('entityId', entityId);
    }

    const response = await apiClient.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data.files;
  }

  async uploadSingleFile(file: File, entityType?: string, entityId?: string): Promise<UploadResponse> {
    const files = await this.uploadFiles([file], entityType, entityId);
    return files[0];
  }

  async deleteFile(fileId: string): Promise<void> {
    await apiClient.delete(`/files/${fileId}`);
  }

  async getFileInfo(fileId: string): Promise<FileInfo> {
    const response = await apiClient.get(`/files/${fileId}`);
    return response.data;
  }

  async getFilesByEntity(entityType: string, entityId: string): Promise<FileInfo[]> {
    const response = await apiClient.get('/files', {
      params: {
        entityType,
        entityId,
      },
    });
    return response.data.files;
  }

  async downloadFile(fileId: string): Promise<Blob> {
    const response = await apiClient.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  getFileUrl(fileId: string): string {
    return `${apiClient.defaults.baseURL}/files/${fileId}/download`;
  }

  // Profile picture specific methods
  async uploadProfilePicture(file: File): Promise<UploadResponse> {
    return this.uploadSingleFile(file, 'user_profile', 'avatar');
  }

  // Course material specific methods
  async uploadCourseMaterial(file: File, courseId: string): Promise<UploadResponse> {
    return this.uploadSingleFile(file, 'course_material', courseId);
  }

  async uploadCourseMedia(files: File[], courseId: string): Promise<UploadResponse[]> {
    return this.uploadFiles(files, 'course_media', courseId);
  }

  // Program document specific methods
  async uploadProgramDocument(file: File, programId: string): Promise<UploadResponse> {
    return this.uploadSingleFile(file, 'program_document', programId);
  }

  // Beneficiary document specific methods
  async uploadBeneficiaryDocument(file: File, beneficiaryId: string): Promise<UploadResponse> {
    return this.uploadSingleFile(file, 'beneficiary_document', beneficiaryId);
  }
}

export const filesApi = new FilesApi();