import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

import { Modal, ConfirmDialog } from '../Modal';

describe('Modal', () => {
  it('renders when isOpen is true', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        <div>Modal Content</div>
      </Modal>
    );

    expect(screen.getByText('Modal Content')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    render(
      <Modal isOpen={false} onClose={() => {}}>
        <div>Modal Content</div>
      </Modal>
    );

    expect(screen.queryByText('Modal Content')).not.toBeInTheDocument();
  });

  it('renders title when provided', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} title="Test Modal">
        <div>Content</div>
      </Modal>
    );

    expect(screen.getByText('Test Modal')).toBeInTheDocument();
  });

  it('calls onClose when clicking backdrop', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose}>
        <div>Content</div>
      </Modal>
    );

    const backdrop = document.querySelector('.bg-black\\/50');
    fireEvent.click(backdrop!);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when clicking X button', async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();

    render(
      <Modal isOpen={true} onClose={onClose} title="Test">
        <div>Content</div>
      </Modal>
    );

    const closeButton = screen.getByRole('button');
    await user.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('does not close when clicking modal content', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose}>
        <div>Content</div>
      </Modal>
    );

    fireEvent.click(screen.getByText('Content'));

    expect(onClose).not.toHaveBeenCalled();
  });

  it('applies different size classes', () => {
    const sizes = ['sm', 'md', 'lg', 'xl'] as const;

    sizes.forEach((size) => {
      const { rerender } = render(
        <Modal isOpen={true} onClose={() => {}} size={size}>
          <div>Content</div>
        </Modal>
      );

      const modal = document.querySelector('.bg-white');
      expect(modal).toHaveClass(
        size === 'sm'
          ? 'max-w-md'
          : size === 'md'
          ? 'max-w-lg'
          : size === 'lg'
          ? 'max-w-2xl'
          : 'max-w-4xl'
      );

      rerender(<div />);
    });
  });
});

describe('ConfirmDialog', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onConfirm: vi.fn(),
    title: 'Confirm Action',
    message: 'Are you sure you want to proceed?',
  };

  it('renders with title and message', () => {
    render(<ConfirmDialog {...defaultProps} />);

    expect(screen.getByText('Confirm Action')).toBeInTheDocument();
    expect(screen.getByText('Are you sure you want to proceed?')).toBeInTheDocument();
  });

  it('renders custom button text', () => {
    render(<ConfirmDialog {...defaultProps} confirmText="Yes, Delete" cancelText="No, Keep" />);

    expect(screen.getByText('Yes, Delete')).toBeInTheDocument();
    expect(screen.getByText('No, Keep')).toBeInTheDocument();
  });

  it('calls onConfirm when clicking confirm button', async () => {
    const onConfirm = vi.fn();
    const user = userEvent.setup();

    render(<ConfirmDialog {...defaultProps} onConfirm={onConfirm} />);

    await user.click(screen.getByText('Confirm'));

    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when clicking cancel button', async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();

    render(<ConfirmDialog {...defaultProps} onClose={onClose} />);

    await user.click(screen.getByText('Cancel'));

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('disables buttons when loading', () => {
    render(<ConfirmDialog {...defaultProps} loading={true} />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeDisabled();
    expect(screen.getByText('Loading...')).toBeDisabled();
  });

  it('applies variant styling', () => {
    const variants = ['danger', 'warning', 'info'] as const;

    variants.forEach((variant) => {
      const { rerender } = render(<ConfirmDialog {...defaultProps} variant={variant} />);

      const confirmButton = screen.getByText('Confirm');

      if (variant === 'danger') {
        expect(confirmButton).toHaveClass('bg-destructive');
      } else if (variant === 'warning') {
        expect(confirmButton).toHaveClass('bg-yellow-600');
      } else {
        expect(confirmButton).toHaveClass('bg-primary');
      }

      rerender(<div />);
    });
  });
});
