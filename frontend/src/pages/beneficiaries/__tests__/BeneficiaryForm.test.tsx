import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/tests/utils/test-utils'
import userEvent from '@testing-library/user-event'
import { useNavigate, useParams } from 'react-router-dom'
import BeneficiaryForm from '../BeneficiaryForm'
import { mockBeneficiary } from '@/tests/mocks/beneficiary'
import * as beneficiaryHooks from '@/hooks/useBeneficiaries'

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: vi.fn(),
    useParams: vi.fn(),
  }
})

// Mock hooks
vi.mock('@/hooks/useBeneficiaries', () => ({
  useBeneficiary: vi.fn(),
  useCreateBeneficiary: vi.fn(),
  useUpdateBeneficiary: vi.fn(),
}))

describe('BeneficiaryForm', () => {
  const mockNavigate = vi.fn()
  const mockCreateMutate = vi.fn()
  const mockUpdateMutate = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useNavigate).mockReturnValue(mockNavigate)
    vi.mocked(useParams).mockReturnValue({})
    
    vi.mocked(beneficiaryHooks.useBeneficiary).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    } as any)
    
    vi.mocked(beneficiaryHooks.useCreateBeneficiary).mockReturnValue({
      mutateAsync: mockCreateMutate,
      isPending: false,
    } as any)
    
    vi.mocked(beneficiaryHooks.useUpdateBeneficiary).mockReturnValue({
      mutateAsync: mockUpdateMutate,
      isPending: false,
    } as any)
  })

  describe('Create Mode', () => {
    it('renders form with correct title', () => {
      render(<BeneficiaryForm />)
      
      expect(screen.getByText('Add New Beneficiary')).toBeInTheDocument()
      expect(screen.getByText('Create a new beneficiary profile')).toBeInTheDocument()
    })

    it('shows required field indicators', () => {
      render(<BeneficiaryForm />)
      
      const requiredLabels = screen.getAllByText('*')
      expect(requiredLabels.length).toBeGreaterThan(0)
    })

    it('validates required fields', async () => {
      const user = userEvent.setup()
      render(<BeneficiaryForm />)
      
      const submitButton = screen.getByText('Create Beneficiary')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText('First name must be at least 2 characters')).toBeInTheDocument()
        expect(screen.getByText('Last name must be at least 2 characters')).toBeInTheDocument()
      })
    })

    it('validates email format', async () => {
      const user = userEvent.setup()
      render(<BeneficiaryForm />)
      
      const emailInput = screen.getByPlaceholderText('john.doe@example.com')
      await user.type(emailInput, 'invalid-email')
      
      const submitButton = screen.getByText('Create Beneficiary')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText('Invalid email address')).toBeInTheDocument()
      })
    })

    it('validates phone format', async () => {
      const user = userEvent.setup()
      render(<BeneficiaryForm />)
      
      const phoneInput = screen.getByPlaceholderText('+33 1 23 45 67 89')
      await user.type(phoneInput, 'invalid-phone')
      
      const submitButton = screen.getByText('Create Beneficiary')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText('Invalid phone number format')).toBeInTheDocument()
      })
    })

    it('submits form with valid data', async () => {
      const user = userEvent.setup()
      mockCreateMutate.mockResolvedValue({})
      
      render(<BeneficiaryForm />)
      
      // Fill required fields
      await user.type(screen.getByPlaceholderText('John'), 'John')
      await user.type(screen.getByPlaceholderText('Doe'), 'Doe')
      
      const submitButton = screen.getByText('Create Beneficiary')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(mockCreateMutate).toHaveBeenCalledWith(
          expect.objectContaining({
            first_name: 'John',
            last_name: 'Doe',
          })
        )
        expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries')
      })
    })

    it('handles tag input correctly', async () => {
      const user = userEvent.setup()
      render(<BeneficiaryForm />)
      
      const tagInputs = screen.getAllByPlaceholderText('Add tag...')
      const mainTagInput = tagInputs[tagInputs.length - 1] // Get the last one (Tags field)
      
      await user.type(mainTagInput, 'test-tag')
      await user.keyboard('{Enter}')
      
      expect(screen.getByText('test-tag')).toBeInTheDocument()
    })

    it('navigates back on cancel', async () => {
      const user = userEvent.setup()
      render(<BeneficiaryForm />)
      
      const cancelButton = screen.getByText('Cancel')
      await user.click(cancelButton)
      
      expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries')
    })
  })

  describe('Edit Mode', () => {
    beforeEach(() => {
      vi.mocked(useParams).mockReturnValue({ id: '1' })
      vi.mocked(beneficiaryHooks.useBeneficiary).mockReturnValue({
        data: { data: { beneficiary: mockBeneficiary } },
        isLoading: false,
        error: null,
      } as any)
    })

    it('renders form with correct title', () => {
      render(<BeneficiaryForm />)
      
      expect(screen.getByText('Edit Beneficiary')).toBeInTheDocument()
      expect(screen.getByText('Update beneficiary information')).toBeInTheDocument()
    })

    it('shows loading state while fetching data', () => {
      vi.mocked(beneficiaryHooks.useBeneficiary).mockReturnValue({
        data: null,
        isLoading: true,
        error: null,
      } as any)
      
      render(<BeneficiaryForm />)
      
      expect(screen.getByRole('status')).toBeInTheDocument()
    })

    it('populates form with existing data', async () => {
      render(<BeneficiaryForm />)
      
      await waitFor(() => {
        expect(screen.getByDisplayValue('John')).toBeInTheDocument()
        expect(screen.getByDisplayValue('Doe')).toBeInTheDocument()
        expect(screen.getByDisplayValue('john.doe@example.com')).toBeInTheDocument()
      })
    })

    it('submits form with updated data', async () => {
      const user = userEvent.setup()
      mockUpdateMutate.mockResolvedValue({})
      
      render(<BeneficiaryForm />)
      
      await waitFor(() => {
        expect(screen.getByDisplayValue('John')).toBeInTheDocument()
      })
      
      // Update first name
      const firstNameInput = screen.getByDisplayValue('John')
      await user.clear(firstNameInput)
      await user.type(firstNameInput, 'Jane')
      
      const submitButton = screen.getByText('Update Beneficiary')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(mockUpdateMutate).toHaveBeenCalledWith({
          id: 1,
          data: expect.objectContaining({
            first_name: 'Jane',
          })
        })
        expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries')
      })
    })
  })

  describe('Role-based Access', () => {
    it('shows status field for admin role', () => {
      render(<BeneficiaryForm />, {
        user: { role: 'admin', primaryRole: 'admin' } as any,
      })
      
      expect(screen.getByLabelText('Status')).toBeInTheDocument()
    })

    it('hides status field for trainer role', () => {
      render(<BeneficiaryForm />, {
        user: { role: 'trainer', primaryRole: 'trainer' } as any,
      })
      
      expect(screen.queryByLabelText('Status')).not.toBeInTheDocument()
    })
  })
})