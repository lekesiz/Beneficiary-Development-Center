import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

import ServerError from '../ServerError';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

describe('ServerError', () => {
  it('renders 500 error page', () => {
    render(<ServerError />);

    expect(screen.getByText('500')).toBeInTheDocument();
    expect(screen.getByText('Internal Server Error')).toBeInTheDocument();
  });
});