import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

import NotFound from '../NotFound';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

describe('NotFound', () => {
  it('renders 404 error page', () => {
    render(<NotFound />);

    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText('Page Not Found')).toBeInTheDocument();
  });
});