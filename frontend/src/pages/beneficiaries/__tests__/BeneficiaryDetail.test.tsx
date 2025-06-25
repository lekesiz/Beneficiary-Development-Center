import userEvent from '@testing-library/user-event';
import { useNavigate, useParams } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';


import * as beneficiaryHooks from '@/hooks/useBeneficiaries';
import { mockBeneficiary } from '@/tests/mocks/beneficiary';
import { render, screen, waitFor } from '@/tests/utils/test-utils';

import BeneficiaryDetail from '../BeneficiaryDetail';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
    useParams: vi.fn(),
  };
});

// Mock hooks
vi.mock('@/hooks/useBeneficiaries', () => ({
  useBeneficiary: vi.fn(),
  useDeleteBeneficiary: vi.fn(),
}));

describe('BeneficiaryDetail', () => {
  const mockNavigate = vi.fn();
  const mockDeleteMutate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useNavigate).mockReturnValue(mockNavigate);
    vi.mocked(useParams).mockReturnValue({ id: '1' });

    vi.mocked(beneficiaryHooks.useBeneficiary).mockReturnValue({
      data: { data: { beneficiary: mockBeneficiary } },
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(beneficiaryHooks.useDeleteBeneficiary).mockReturnValue({
      mutateAsync: mockDeleteMutate,
      isPending: false,
    } as any);
  });

  it('shows loading state', () => {
    vi.mocked(beneficiaryHooks.useBeneficiary).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    } as any);

    render(<BeneficiaryDetail />);

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows error state when beneficiary not found', () => {
    vi.mocked(beneficiaryHooks.useBeneficiary).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Not found'),
    } as any);

    render(<BeneficiaryDetail />);

    expect(screen.getByText('Beneficiary not found')).toBeInTheDocument();
    expect(
      screen.getByText(/doesn't exist or you don't have permission/)
    ).toBeInTheDocument();
  });

  it('displays beneficiary basic information', () => {
    render(<BeneficiaryDetail />);

    // Header
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
    expect(screen.getByText('ID: EXT001')).toBeInTheDocument();

    // Basic info
    expect(screen.getByText('john.doe@example.com')).toBeInTheDocument();
    expect(screen.getByText('+33123456789')).toBeInTheDocument();
    expect(screen.getByText('+33612345678')).toBeInTheDocument();
    expect(screen.getByText('34 years')).toBeInTheDocument();
    expect(screen.getByText('male')).toBeInTheDocument();
    expect(screen.getByText('French')).toBeInTheDocument();
    expect(screen.getByText('Paris, France')).toBeInTheDocument();
  });

  it('displays address information', () => {
    render(<BeneficiaryDetail />);

    expect(screen.getByText('123 Main Street')).toBeInTheDocument();
    expect(screen.getByText('Paris, Île-de-France, 75001')).toBeInTheDocument();
    expect(screen.getByText('France')).toBeInTheDocument();
  });

  it('displays professional information', () => {
    render(<BeneficiaryDetail />);

    expect(screen.getByText('Employed')).toBeInTheDocument();
    expect(screen.getByText('Software Developer')).toBeInTheDocument();
    expect(screen.getByText('Tech Corp')).toBeInTheDocument();
    expect(screen.getByText('Technology')).toBeInTheDocument();
    expect(screen.getByText('5 years')).toBeInTheDocument();
  });

  it('displays education information', () => {
    render(<BeneficiaryDetail />);

    expect(screen.getByText('Bachelor')).toBeInTheDocument();
    expect(screen.getByText('Computer Science')).toBeInTheDocument();
    expect(screen.getByText('AWS Certified')).toBeInTheDocument();
    expect(screen.getByText('Scrum Master')).toBeInTheDocument();
  });

  it('displays skills, interests, and goals', () => {
    render(<BeneficiaryDetail />);

    // Skills
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Node.js')).toBeInTheDocument();

    // Interests
    expect(screen.getByText('Web Development')).toBeInTheDocument();
    expect(screen.getByText('AI')).toBeInTheDocument();
    expect(screen.getByText('Open Source')).toBeInTheDocument();

    // Goals
    expect(screen.getByText('Learn Machine Learning')).toBeInTheDocument();
    expect(screen.getByText('Start a tech startup')).toBeInTheDocument();
  });

  it('displays management information', () => {
    render(<BeneficiaryDetail />);

    expect(screen.getByText('Jane Trainer')).toBeInTheDocument();
    expect(screen.getByText('developer')).toBeInTheDocument();
    expect(screen.getByText('remote')).toBeInTheDocument();
    expect(screen.getByText('experienced')).toBeInTheDocument();
  });

  it('displays progress summary', () => {
    render(<BeneficiaryDetail />);

    expect(screen.getByText('75%')).toBeInTheDocument();
    expect(screen.getByText('Overall Progress')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // Active enrollments
    expect(screen.getByText('1')).toBeInTheDocument(); // Completed programs
  });

  it('displays notes', () => {
    render(<BeneficiaryDetail />);

    expect(
      screen.getByText('Initial assessment completed')
    ).toBeInTheDocument();
  });

  it('navigates back when clicking back button', async () => {
    const user = userEvent.setup();
    render(<BeneficiaryDetail />);

    const backButton = screen.getByText('Back to Beneficiaries');
    await user.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries');
  });

  describe('Role-based Actions', () => {
    it('shows edit and delete buttons for admin', () => {
      render(<BeneficiaryDetail />, {
        user: { role: 'admin', primaryRole: 'admin' } as any,
      });

      expect(screen.getByText('Edit')).toBeInTheDocument();
      expect(screen.getByText('Delete')).toBeInTheDocument();
    });

    it('shows only edit button for trainer', () => {
      render(<BeneficiaryDetail />, {
        user: { role: 'trainer', primaryRole: 'trainer' } as any,
      });

      expect(screen.getByText('Edit')).toBeInTheDocument();
      expect(screen.queryByText('Delete')).not.toBeInTheDocument();
    });

    it('hides action buttons for student', () => {
      render(<BeneficiaryDetail />, {
        user: { role: 'student', primaryRole: 'student' } as any,
      });

      expect(screen.queryByText('Edit')).not.toBeInTheDocument();
      expect(screen.queryByText('Delete')).not.toBeInTheDocument();
    });
  });

  describe('Actions', () => {
    it('navigates to edit page when clicking edit button', async () => {
      const user = userEvent.setup();
      render(<BeneficiaryDetail />);

      const editButton = screen.getByText('Edit');
      await user.click(editButton);

      expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries/1/edit');
    });

    it('shows delete confirmation dialog', async () => {
      const user = userEvent.setup();
      render(<BeneficiaryDetail />);

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      expect(screen.getByText('Delete Beneficiary')).toBeInTheDocument();
      expect(
        screen.getByText(/Are you sure you want to delete John Doe/)
      ).toBeInTheDocument();
    });

    it('deletes beneficiary on confirmation', async () => {
      const user = userEvent.setup();
      mockDeleteMutate.mockResolvedValue({});

      render(<BeneficiaryDetail />);

      // Open dialog
      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      // Confirm deletion
      const confirmButton = screen.getAllByText('Delete')[1]; // Second delete button in dialog
      await user.click(confirmButton);

      await waitFor(() => {
        expect(mockDeleteMutate).toHaveBeenCalledWith(1);
        expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries');
      });
    });

    it('closes delete dialog on cancel', async () => {
      const user = userEvent.setup();
      render(<BeneficiaryDetail />);

      // Open dialog
      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      // Cancel
      const cancelButton = screen.getByText('Cancel');
      await user.click(cancelButton);

      await waitFor(() => {
        expect(
          screen.queryByText('Delete Beneficiary')
        ).not.toBeInTheDocument();
      });
    });
  });
});
