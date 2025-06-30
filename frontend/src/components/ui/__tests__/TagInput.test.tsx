import { render, screen, fireEvent, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

import { TagInput } from '../TagInput';

describe('TagInput', () => {
  it('renders with placeholder', () => {
    render(<TagInput value={[]} onChange={() => {}} placeholder="Add a tag..." />);

    expect(screen.getByPlaceholderText('Add a tag...')).toBeInTheDocument();
  });

  it('displays existing tags', () => {
    const tags = ['react', 'typescript', 'testing'];
    render(<TagInput value={tags} onChange={() => {}} />);

    tags.forEach((tag) => {
      expect(screen.getByText(tag)).toBeInTheDocument();
    });
  });

  it('adds tag on Enter key', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TagInput value={[]} onChange={onChange} />);

    const input = screen.getByRole('textbox');
    await act(async () => {
      await user.type(input, 'new-tag');
      await user.keyboard('{Enter}');
    });

    expect(onChange).toHaveBeenCalledWith(['new-tag']);
  });

  it('adds tag on comma key', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TagInput value={[]} onChange={onChange} />);

    const input = screen.getByRole('textbox');
    await user.type(input, 'new-tag,');

    expect(onChange).toHaveBeenCalledWith(['new-tag']);
  });

  it('adds tag on blur', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TagInput value={[]} onChange={onChange} />);

    const input = screen.getByRole('textbox');
    await user.type(input, 'new-tag');
    fireEvent.blur(input);

    expect(onChange).toHaveBeenCalledWith(['new-tag']);
  });

  it('removes tag when clicking X button', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TagInput value={['tag1', 'tag2', 'tag3']} onChange={onChange} />);

    const removeButtons = screen.getAllByRole('button');
    await user.click(removeButtons[1]); // Remove 'tag2'

    expect(onChange).toHaveBeenCalledWith(['tag1', 'tag3']);
  });

  it('prevents duplicate tags', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TagInput value={['existing-tag']} onChange={onChange} />);

    const input = screen.getByRole('textbox');
    await user.type(input, 'existing-tag');
    await user.keyboard('{Enter}');

    expect(onChange).not.toHaveBeenCalled();
  });

  it('trims whitespace from tags', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TagInput value={[]} onChange={onChange} />);

    const input = screen.getByRole('textbox');
    await user.type(input, '  spaced-tag  ');
    await user.keyboard('{Enter}');

    expect(onChange).toHaveBeenCalledWith(['spaced-tag']);
  });

  it('removes last tag on Backspace when input is empty', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TagInput value={['tag1', 'tag2', 'tag3']} onChange={onChange} />);

    const input = screen.getByRole('textbox');
    await user.click(input);
    await user.keyboard('{Backspace}');

    expect(onChange).toHaveBeenCalledWith(['tag1', 'tag2']);
  });

  it('applies error styling when error prop is true', () => {
    render(<TagInput value={[]} onChange={() => {}} error />);

    const container = screen.getByRole('textbox').parentElement;
    expect(container).toHaveClass('border-destructive');
  });
});
