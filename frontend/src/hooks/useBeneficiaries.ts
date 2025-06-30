import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

import { beneficiariesApi } from '@/api/beneficiaries';
import { BeneficiaryCreate, BeneficiaryUpdate, BeneficiaryListParams } from '@/types/beneficiary';

// Query keys
export const beneficiaryKeys = {
  all: ['beneficiaries'] as const,
  lists: () => [...beneficiaryKeys.all, 'list'] as const,
  list: (params: BeneficiaryListParams) => [...beneficiaryKeys.lists(), params] as const,
  details: () => [...beneficiaryKeys.all, 'detail'] as const,
  detail: (id: number) => [...beneficiaryKeys.details(), id] as const,
  statistics: () => [...beneficiaryKeys.all, 'statistics'] as const,
};

// Get all beneficiaries
export const useBeneficiaries = (params?: BeneficiaryListParams) => {
  return useQuery({
    queryKey: beneficiaryKeys.list(params || {}),
    queryFn: () => beneficiariesApi.getAll(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Get beneficiary by ID
export const useBeneficiary = (id: number, enabled = true) => {
  return useQuery({
    queryKey: beneficiaryKeys.detail(id),
    queryFn: () => beneficiariesApi.getById(id),
    enabled: enabled && !!id,
    staleTime: 5 * 60 * 1000,
  });
};

// Get beneficiary statistics
export const useBeneficiaryStatistics = () => {
  return useQuery({
    queryKey: beneficiaryKeys.statistics(),
    queryFn: () => beneficiariesApi.getStatistics(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Create beneficiary
export const useCreateBeneficiary = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: BeneficiaryCreate) => beneficiariesApi.create(data),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.statistics() });
      toast.success(response.data.message || 'Beneficiary created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create beneficiary');
    },
  });
};

// Update beneficiary
export const useUpdateBeneficiary = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: BeneficiaryUpdate }) =>
      beneficiariesApi.update(id, data),
    onSuccess: (response, { id }) => {
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.detail(id) });
      toast.success(response.data.message || 'Beneficiary updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update beneficiary');
    },
  });
};

// Delete beneficiary
export const useDeleteBeneficiary = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => beneficiariesApi.delete(id),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.statistics() });
      toast.success(response.data.message || 'Beneficiary deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to delete beneficiary');
    },
  });
};

// Add note to beneficiary
export const useAddNote = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, note }: { id: number; note: string }) => beneficiariesApi.addNote(id, note),
    onSuccess: (response, { id }) => {
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.detail(id) });
      toast.success('Note added successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to add note');
    },
  });
};

// Add tag to beneficiary
export const useAddTag = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, tag }: { id: number; tag: string }) => beneficiariesApi.addTag(id, tag),
    onSuccess: (response, { id }) => {
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.lists() });
      toast.success('Tag added successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to add tag');
    },
  });
};

// Remove tag from beneficiary
export const useRemoveTag = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, tag }: { id: number; tag: string }) => beneficiariesApi.removeTag(id, tag),
    onSuccess: (response, { id }) => {
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.lists() });
      toast.success('Tag removed successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to remove tag');
    },
  });
};

// Assign trainer to beneficiary
export const useAssignTrainer = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, trainerId }: { id: number; trainerId: number }) =>
      beneficiariesApi.assignTrainer(id, trainerId),
    onSuccess: (response, { id }) => {
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: beneficiaryKeys.lists() });
      toast.success('Trainer assigned successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to assign trainer');
    },
  });
};
