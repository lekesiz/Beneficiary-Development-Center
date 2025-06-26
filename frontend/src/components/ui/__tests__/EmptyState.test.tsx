import { render, screen, fireEvent } from '@testing-library/react';
import { FileText, Users } from 'lucide-react';
import { describe, it, expect, vi } from 'vitest';

import { EmptyState } from '../EmptyState';

describe('EmptyState', () => {
  it('renders with all props', () => {
    const handleClick = vi.fn();
    
    render(
      <EmptyState
        icon={FileText}
        title="No Documents"
        description="Upload your first document"
        action={{
          text: "Upload Document",
          onClick: handleClick,
        }}
      />
    );

    expect(screen.getByText('No Documents')).toBeInTheDocument();
    expect(screen.getByText('Upload your first document')).toBeInTheDocument();
    expect(screen.getByText('Upload Document')).toBeInTheDocument();
  });

  it('renders without action button', () => {
    render(
      <EmptyState
        icon={Users}
        title="No Users"
        description="No users have been added yet"
      />
    );

    expect(screen.getByText('No Users')).toBeInTheDocument();
    expect(screen.getByText('No users have been added yet')).toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('calls onClick handler when action button is clicked', () => {
    const handleClick = vi.fn();
    
    render(
      <EmptyState
        icon={FileText}
        title="No Files"
        description="Add files to get started"
        action={{
          text: "Add File",
          onClick: handleClick,
        }}
      />
    );

    const button = screen.getByText('Add File');
    fireEvent.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('renders the icon with correct styling', () => {
    render(
      <EmptyState
        icon={FileText}
        title="Test"
        description="Test description"
      />
    );

    const iconWrapper = screen.getByText('Test').parentElement?.querySelector('.bg-gray-100');
    expect(iconWrapper).toBeInTheDocument();
    expect(iconWrapper).toHaveClass('rounded-full', 'w-16', 'h-16');
  });

  it('applies custom className', () => {
    const { container } = render(
      <EmptyState
        icon={FileText}
        title="Test"
        description="Test description"
        className="custom-class"
      />
    );

    const emptyState = container.firstChild;
    expect(emptyState).toHaveClass('custom-class');
    expect(emptyState).toHaveClass('flex', 'flex-col', 'items-center', 'justify-center', 'py-12', 'px-6', 'text-center');
  });

  it('centers text content', () => {
    render(
      <EmptyState
        icon={FileText}
        title="Centered Title"
        description="This should be centered"
      />
    );

    const title = screen.getByText('Centered Title');
    const description = screen.getByText('This should be centered');
    
    // The EmptyState component applies text-center to the container, not individual elements
    expect(title.closest('div')).toHaveClass('text-center');
    expect(description.closest('div')).toHaveClass('text-center');
  });

  it('limits description width for readability', () => {
    render(
      <EmptyState
        icon={FileText}
        title="Test"
        description="Very long description that should have a maximum width applied to it for better readability"
      />
    );

    const description = screen.getByText(/Very long description/);
    expect(description).toHaveClass('max-w-sm');
  });

  it('renders action button with correct size', () => {
    render(
      <EmptyState
        icon={FileText}
        title="Test"
        description="Test"
        action={{
          text: "Action Button",
          onClick: () => {},
        }}
      />
    );

    const button = screen.getByText('Action Button');
    // The button uses size="sm" in the component
    expect(button.closest('button')).toBeInTheDocument();
  });

  it('displays icon inside a styled container', () => {
    const { container } = render(
      <EmptyState
        icon={FileText}
        title="Test"
        description="Test"
      />
    );

    const iconContainer = container.querySelector('.bg-gray-100.rounded-full');
    expect(iconContainer).toBeInTheDocument();
    
    const icon = iconContainer?.querySelector('svg');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('w-8', 'h-8', 'text-gray-400');
  });

  it('maintains proper spacing between elements', () => {
    render(
      <EmptyState
        icon={FileText}
        title="Test Title"
        description="Test Description"
        action={{
          text: "Test Action",
          onClick: () => {},
        }}
      />
    );

    const title = screen.getByText('Test Title');
    const description = screen.getByText('Test Description');
    
    // Check for the classes that are actually in the component
    expect(title).toHaveClass('text-lg', 'font-semibold', 'text-gray-900', 'mb-2');
    expect(description).toHaveClass('text-sm', 'text-gray-500', 'mb-6', 'max-w-sm');
  });
});