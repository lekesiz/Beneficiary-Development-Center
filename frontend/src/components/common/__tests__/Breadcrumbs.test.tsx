import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';

import { Breadcrumbs } from '../Breadcrumbs';

// Store the current test path
let currentTestPath = '/';

// Mock the useBreadcrumbs hook directly
vi.mock('@/hooks/useBreadcrumbs', () => ({
  useBreadcrumbs: vi.fn(() => {
    if (currentTestPath === '/dashboard') {
      // Return single active breadcrumb for dashboard - this should not render
      return [{ label: 'Dashboard', path: '/dashboard', isActive: true }];
    }
    
    const breadcrumbs = [
      { label: 'Dashboard', path: '/dashboard', isActive: false },
    ];
    
    if (currentTestPath.includes('/programs')) {
      breadcrumbs.push({ label: 'Programs', path: '/programs', isActive: currentTestPath === '/programs' });
      
      if (currentTestPath.includes('/new')) {
        breadcrumbs.push({ label: 'New Program', path: currentTestPath, isActive: true });
      } else if (currentTestPath.includes('/edit')) {
        breadcrumbs.push({ label: 'Test Program', path: currentTestPath.replace('/edit', ''), isActive: false });
        breadcrumbs.push({ label: 'Edit', path: currentTestPath, isActive: true });
      } else if (currentTestPath !== '/programs') {
        breadcrumbs.push({ label: 'Test Program', path: currentTestPath, isActive: true });
      }
    }
    
    return breadcrumbs;
  }),
}));

const mockQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithRouter = (initialPath: string) => {
  currentTestPath = initialPath;
  return render(
    <QueryClientProvider client={mockQueryClient}>
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route path="*" element={<Breadcrumbs />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('Breadcrumbs', () => {
  it('should not render breadcrumbs on dashboard', () => {
    renderWithRouter('/dashboard');
    expect(screen.queryByRole('navigation', { name: 'Breadcrumb' })).not.toBeInTheDocument();
  });

  it('should render breadcrumbs for programs list', () => {
    renderWithRouter('/programs');
    expect(screen.getByRole('navigation', { name: 'Breadcrumb' })).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Programs')).toBeInTheDocument();
  });

  it('should render breadcrumbs with dynamic program name', () => {
    renderWithRouter('/programs/123');
    expect(screen.getByRole('navigation', { name: 'Breadcrumb' })).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Programs')).toBeInTheDocument();
    // The dynamic name would be fetched from the API
  });

  it('should render breadcrumbs for nested routes', () => {
    renderWithRouter('/programs/123/edit');
    expect(screen.getByRole('navigation', { name: 'Breadcrumb' })).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Programs')).toBeInTheDocument();
  });

  it('should make the last breadcrumb non-clickable', () => {
    renderWithRouter('/programs');
    const programsBreadcrumb = screen.getByText('Programs');
    expect(programsBreadcrumb.closest('a')).not.toBeInTheDocument();
    expect(programsBreadcrumb.closest('span')).toBeInTheDocument();
  });

  it('should make non-last breadcrumbs clickable', () => {
    renderWithRouter('/programs/new');
    const dashboardLink = screen.getByText('Dashboard').closest('a');
    expect(dashboardLink).toBeInTheDocument();
    expect(dashboardLink).toHaveAttribute('href', '/dashboard');
  });

  it('should render home icon for dashboard breadcrumb', () => {
    renderWithRouter('/programs');
    const navigation = screen.getByRole('navigation', { name: 'Breadcrumb' });
    const homeIcon = navigation.querySelector('svg');
    expect(homeIcon).toBeInTheDocument();
  });

  it('should render chevron separators between breadcrumbs', () => {
    renderWithRouter('/programs/new');
    const navigation = screen.getByRole('navigation', { name: 'Breadcrumb' });
    // Look for ChevronRight icons (they have specific classes)
    const chevrons = navigation.querySelectorAll('.mx-1');
    expect(chevrons.length).toBeGreaterThan(0);
  });

  it('should support custom className', () => {
    currentTestPath = '/programs';
    render(
      <QueryClientProvider client={mockQueryClient}>
        <MemoryRouter initialEntries={['/programs']}>
          <Routes>
            <Route path="*" element={<Breadcrumbs className="custom-class" />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );
    const navigation = screen.getByRole('navigation', { name: 'Breadcrumb' });
    expect(navigation).toHaveClass('custom-class');
  });
});