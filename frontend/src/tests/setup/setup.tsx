import '@testing-library/jest-dom';
import * as matchers from '@testing-library/jest-dom/matchers';
import { cleanup, render } from '@testing-library/react';
import { expect, afterEach, beforeAll, afterAll, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import React, { ReactElement } from 'react';

// Mock environment variables FIRST, before any other imports
vi.mock('import.meta', () => ({
  env: {
    VITE_API_URL: 'http://localhost:5001/api/v1',
  },
}));

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers);

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock context providers to avoid dependency issues
vi.mock('@/contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
  useAuth: () => ({
    user: {
      id: 1,
      role: 'admin',
      primaryRole: 'admin',
      email: 'test@example.com',
      firstName: 'Test',
      lastName: 'User',
    },
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    updateProfile: vi.fn(),
  }),
}));

vi.mock('@/contexts/I18nContext', () => ({
  I18nProvider: ({ children }: { children: React.ReactNode }) => children,
  useI18n: () => ({ t: (key: string) => key }),
}));

vi.mock('@/contexts/SocketContext', () => ({
  SocketProvider: ({ children }: { children: React.ReactNode }) => children,
  useSocket: () => ({ socket: null }),
}));

vi.mock('@/contexts/ThemeContext', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
  useTheme: () => ({ theme: 'light', setTheme: vi.fn() }),
}));

// Initialize MSW after environment variables are mocked
import { server } from '../mocks/server';

// MSW Server Lifecycle
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterAll(() => server.close());

// Clean up after each test
afterEach(() => {
  cleanup();
  server.resetHandlers();
});

// Test utilities
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      gcTime: 0,
    },
    mutations: {
      retry: false,
    },
  },
});

export const renderWithProviders = (ui: ReactElement, options?: { initialEntries?: string[] }) => {
  const queryClient = createTestQueryClient();
  
  const AllTheProviders = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={options?.initialEntries || ['/']}>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );

  return {
    ...render(ui, { wrapper: AllTheProviders }),
    queryClient,
  };
};
