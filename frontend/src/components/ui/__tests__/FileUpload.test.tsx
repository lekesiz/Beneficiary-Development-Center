import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { FileUpload } from '../FileUpload';

describe('FileUpload', () => {
  const mockOnUpload = vi.fn();
  const mockOnRemove = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const defaultProps = {
    onUpload: mockOnUpload,
    onRemove: mockOnRemove,
  };

  it('renders upload area with default text', () => {
    render(<FileUpload {...defaultProps} />);

    expect(screen.getByText('Drag and drop files here, or click to select')).toBeInTheDocument();
    expect(screen.getByText('Select Files')).toBeInTheDocument();
  });

  it('shows file size and type restrictions', () => {
    render(
      <FileUpload
        {...defaultProps}
        maxSize={5 * 1024 * 1024} // 5MB
        acceptedTypes={['image/*', 'application/pdf']}
      />
    );

    expect(screen.getByText('Accepted: image/*, application/pdf')).toBeInTheDocument();
    expect(screen.getByText('Max size: 5 MB')).toBeInTheDocument();
  });

  it('handles file selection through input', async () => {
    const user = userEvent.setup();
    mockOnUpload.mockResolvedValue([
      { id: '1', name: 'test.txt', size: 100, type: 'text/plain', url: 'test-url' },
    ]);

    render(<FileUpload {...defaultProps} />);

    const input = screen
      .getByRole('button', { name: /select files/i })
      .querySelector('input[type="file"]');
    expect(input).toBeInTheDocument();

    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });

    // Create a FileList-like object with the file
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    });

    // Trigger the change event
    fireEvent.change(input!);

    await waitFor(() => {
      expect(mockOnUpload).toHaveBeenCalledWith([file]);
    });
  });

  it('validates file size', async () => {
    render(
      <FileUpload
        {...defaultProps}
        maxSize={100} // 100 bytes
      />
    );

    const input = screen
      .getByRole('button', { name: /select files/i })
      .querySelector('input[type="file"]');
    const largeFile = new File(['x'.repeat(200)], 'large.txt', { type: 'text/plain' });

    Object.defineProperty(input, 'files', {
      value: [largeFile],
      writable: false,
    });

    fireEvent.change(input!);

    await waitFor(() => {
      expect(screen.getByText(/File size exceeds/)).toBeInTheDocument();
    });

    expect(mockOnUpload).not.toHaveBeenCalled();
  });

  it('validates file type', async () => {
    render(<FileUpload {...defaultProps} acceptedTypes={['image/*']} />);

    const input = screen
      .getByRole('button', { name: /select files/i })
      .querySelector('input[type="file"]');
    const textFile = new File(['test'], 'test.txt', { type: 'text/plain' });

    Object.defineProperty(input, 'files', {
      value: [textFile],
      writable: false,
    });

    fireEvent.change(input!);

    await waitFor(() => {
      expect(screen.getByText(/File type text\/plain is not accepted/)).toBeInTheDocument();
    });

    expect(mockOnUpload).not.toHaveBeenCalled();
  });

  it('enforces maximum file limit', async () => {
    render(
      <FileUpload
        {...defaultProps}
        maxFiles={2}
        uploadedFiles={[
          { id: '1', name: 'existing.txt', size: 100, type: 'text/plain', url: 'url1' },
          { id: '2', name: 'existing2.txt', size: 100, type: 'text/plain', url: 'url2' },
        ]}
      />
    );

    expect(screen.getByText('Maximum 2 files reached')).toBeInTheDocument();

    // When max files are reached, the Select Files button is not rendered
    expect(screen.queryByText('Select Files')).not.toBeInTheDocument();
  });

  it('displays uploaded files with preview', () => {
    const uploadedFiles = [
      { id: '1', name: 'document.pdf', size: 1024000, type: 'application/pdf', url: 'url1' },
      { id: '2', name: 'image.jpg', size: 500000, type: 'image/jpeg', url: 'url2' },
    ];

    render(<FileUpload {...defaultProps} uploadedFiles={uploadedFiles} showPreview={true} />);

    expect(screen.getByText('Uploaded Files (2)')).toBeInTheDocument();
    expect(screen.getByText('document.pdf')).toBeInTheDocument();
    expect(screen.getByText('1000 KB')).toBeInTheDocument();
    expect(screen.getByText('image.jpg')).toBeInTheDocument();
    expect(screen.getByText('488.28 KB')).toBeInTheDocument();
  });

  it('shows file progress indicators', () => {
    const uploadedFiles = [
      { id: '1', name: 'uploading.txt', size: 1000, type: 'text/plain', progress: 50 },
    ];

    render(<FileUpload {...defaultProps} uploadedFiles={uploadedFiles} />);

    // Check for the progress bar div with specific width style
    const progressBar = document.querySelector('[style*="width: 50%"]');
    expect(progressBar).toBeInTheDocument();
  });

  it('shows file errors', () => {
    const uploadedFiles = [
      { id: '1', name: 'failed.txt', size: 1000, type: 'text/plain', error: 'Upload failed' },
    ];

    render(<FileUpload {...defaultProps} uploadedFiles={uploadedFiles} />);

    expect(screen.getByText('Upload failed')).toBeInTheDocument();
  });

  it('handles file removal', async () => {
    const user = userEvent.setup();
    const uploadedFiles = [
      { id: '1', name: 'test.txt', size: 1000, type: 'text/plain', url: 'url1' },
    ];

    render(<FileUpload {...defaultProps} uploadedFiles={uploadedFiles} />);

    const removeButton = screen.getByRole('button', { name: '' }); // X button
    await user.click(removeButton);

    expect(mockOnRemove).toHaveBeenCalledWith('1');
  });

  it('handles drag and drop', async () => {
    mockOnUpload.mockResolvedValue([
      { id: '1', name: 'dropped.txt', size: 100, type: 'text/plain', url: 'url' },
    ]);

    render(<FileUpload {...defaultProps} />);

    const dropArea = screen.getByText(/drag and drop files here/i).closest('div')?.parentElement;
    expect(dropArea).toBeInTheDocument();

    const file = new File(['test'], 'dropped.txt', { type: 'text/plain' });
    const dataTransfer = {
      files: [file],
      types: ['Files'],
      dropEffect: 'copy',
      effectAllowed: 'all',
    };

    fireEvent.dragOver(dropArea!, {
      dataTransfer,
    });

    fireEvent.drop(dropArea!, {
      dataTransfer,
    });

    await waitFor(() => {
      expect(mockOnUpload).toHaveBeenCalledWith([file]);
    });
  });

  it('prevents drag and drop when disabled', () => {
    render(<FileUpload {...defaultProps} disabled={true} />);

    // When disabled, the component still shows the drop area but it's disabled
    const dropArea = document.querySelector('.border-dashed');
    expect(dropArea).toBeInTheDocument();
    expect(dropArea).toHaveClass('opacity-50');
    expect(dropArea).toHaveClass('cursor-not-allowed');

    // Verify drag events don't change state when disabled
    fireEvent.dragOver(dropArea!);

    // Should not add the drag-over styling
    expect(dropArea).not.toHaveClass('border-primary');
  });

  it('dismisses error messages', async () => {
    const user = userEvent.setup();
    render(<FileUpload {...defaultProps} maxSize={100} />);

    const input = screen
      .getByRole('button', { name: /select files/i })
      .querySelector('input[type="file"]');
    const largeFile = new File(['x'.repeat(200)], 'large.txt', { type: 'text/plain' });

    Object.defineProperty(input, 'files', {
      value: [largeFile],
      writable: false,
    });

    fireEvent.change(input!);

    await waitFor(() => {
      expect(screen.getByText(/File size exceeds/)).toBeInTheDocument();
    });

    const dismissButton = screen.getByText('Dismiss');

    await act(async () => {
      await user.click(dismissButton);
    });

    expect(screen.queryByText(/File size exceeds/)).not.toBeInTheDocument();
  });

  it('opens file URL when view button is clicked', async () => {
    const user = userEvent.setup();
    const mockOpen = vi.spyOn(window, 'open').mockImplementation(() => null);

    const uploadedFiles = [
      {
        id: '1',
        name: 'test.txt',
        size: 1000,
        type: 'text/plain',
        url: 'https://example.com/file.txt',
      },
    ];

    render(<FileUpload {...defaultProps} uploadedFiles={uploadedFiles} />);

    const viewButton = screen.getByText('View');
    await user.click(viewButton);

    expect(mockOpen).toHaveBeenCalledWith('https://example.com/file.txt', '_blank');

    mockOpen.mockRestore();
  });

  it('works in single file mode', async () => {
    mockOnUpload.mockResolvedValue([
      { id: '1', name: 'single.txt', size: 100, type: 'text/plain', url: 'url' },
    ]);

    render(<FileUpload {...defaultProps} multiple={false} maxFiles={1} />);

    const input = screen
      .getByRole('button', { name: /select files/i })
      .querySelector('input[type="file"]');
    expect(input).not.toHaveAttribute('multiple');

    const file = new File(['test'], 'single.txt', { type: 'text/plain' });

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(input!);

    await waitFor(() => {
      expect(mockOnUpload).toHaveBeenCalledWith([file]);
    });
  });

  it('formats file sizes correctly', () => {
    const testCases = [
      { bytes: 0, expected: '0 Bytes' },
      { bytes: 512, expected: '512 Bytes' },
      { bytes: 1024, expected: '1 KB' },
      { bytes: 1536, expected: '1.5 KB' },
      { bytes: 1048576, expected: '1 MB' },
      { bytes: 1073741824, expected: '1 GB' },
    ];

    testCases.forEach(({ bytes, expected }) => {
      const uploadedFiles = [
        { id: '1', name: 'test.txt', size: bytes, type: 'text/plain', url: 'url' },
      ];

      const { unmount } = render(<FileUpload {...defaultProps} uploadedFiles={uploadedFiles} />);

      expect(screen.getByText(expected)).toBeInTheDocument();
      unmount();
    });
  });
});
