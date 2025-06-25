import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

import Unauthorized from '../Unauthorized';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

describe('Unauthorized', () => {
  it('renders 403 error page', () => {
    render(<Unauthorized />);

    expect(screen.getByText('403')).toBeInTheDocument();
    expect(screen.getByText('Access Denied')).toBeInTheDocument();
  });
});