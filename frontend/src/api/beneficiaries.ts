import {
  Beneficiary,
  BeneficiaryCreate,
  BeneficiaryUpdate,
  BeneficiaryListParams,
  BeneficiaryListResponse,
  BeneficiaryStatistics,
} from '@/types/beneficiary';

import apiClient from './client';

export const beneficiariesApi = {
  // Get all beneficiaries with pagination and filters
  getAll: (params?: BeneficiaryListParams) => {
    return apiClient.get<BeneficiaryListResponse>('/beneficiaries', { params });
  },

  // Get beneficiary by ID
  getById: (id: number) => {
    return apiClient.get<{ beneficiary: Beneficiary }>(`/beneficiaries/${id}`);
  },

  // Get beneficiary by UUID
  getByUuid: (uuid: string) => {
    return apiClient.get<{ beneficiary: Beneficiary }>(`/beneficiaries/uuid/${uuid}`);
  },

  // Create new beneficiary
  create: (data: BeneficiaryCreate) => {
    return apiClient.post<{ message: string; beneficiary: Beneficiary }>('/beneficiaries', data);
  },

  // Update beneficiary
  update: (id: number, data: BeneficiaryUpdate) => {
    return apiClient.put<{ message: string; beneficiary: Beneficiary }>(
      `/beneficiaries/${id}`,
      data
    );
  },

  // Delete beneficiary (soft delete)
  delete: (id: number) => {
    return apiClient.delete<{ message: string }>(`/beneficiaries/${id}`);
  },

  // Add note to beneficiary
  addNote: (id: number, note: string) => {
    return apiClient.post<{ message: string; beneficiary: Beneficiary }>(
      `/beneficiaries/${id}/notes`,
      { note }
    );
  },

  // Add tag to beneficiary
  addTag: (id: number, tag: string) => {
    return apiClient.post<{ message: string; beneficiary: Beneficiary }>(
      `/beneficiaries/${id}/tags`,
      { tag }
    );
  },

  // Remove tag from beneficiary
  removeTag: (id: number, tag: string) => {
    return apiClient.delete<{ message: string; beneficiary: Beneficiary }>(
      `/beneficiaries/${id}/tags/${tag}`
    );
  },

  // Get beneficiary statistics
  getStatistics: () => {
    return apiClient.get<{ statistics: BeneficiaryStatistics }>('/beneficiaries/statistics');
  },

  // Assign trainer to beneficiary
  assignTrainer: (id: number, trainerId: number) => {
    return apiClient.post<{ message: string; beneficiary: Beneficiary }>(
      `/beneficiaries/${id}/assign-trainer`,
      { trainer_id: trainerId }
    );
  },
};
