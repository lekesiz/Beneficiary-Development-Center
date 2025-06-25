import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, RenderOptions } from '@testing-library/react';
import * as React from 'react';
import { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';

import { User } from '@/types/user';

// Create a custom render function that includes all providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  user?: Partial<User>;
  initialRoute?: string;
}

// Default test user
const defaultUser: User = {
  id: 1,
  uuid: 'test-uuid',
  email: 'test@example.com',
  firstName: 'Test',
  lastName: 'User',
  first_name: 'Test',
  last_name: 'User',
  fullName: 'Test User',
  isActive: true,
  isVerified: true,
  twoFactorEnabled: false,
  preferences: {
    language: 'en',
    theme: 'light',
    emailFrequency: 'daily',
    timezone: 'UTC',
  },
  notificationSettings: {
    email: true,
    inApp: true,
    sms: false,
    evaluationReminders: true,
    appointmentReminders: true,
    newContent: true,
  },
  tenantId: 1,
  tenant_id: 1,
  primaryRole: 'admin',
  role: 'admin',
  roles: [{ id: 1, name: 'admin', description: 'Administrator' }],
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
};

// Mock the context providers to avoid dependency issues
const MockAuthProvider = ({ children, value }: { children: React.ReactNode; value?: any }) => {
  const mockValue = value || {
    user: defaultUser,
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    updateProfile: vi.fn(),
  };
  
  // Create a React context to provide the mock value
  const AuthContext = React.createContext(mockValue);
  return <AuthContext.Provider value={mockValue}>{children}</AuthContext.Provider>;
};

const MockI18nProvider = ({ children }: { children: React.ReactNode }) => (
  <div data-testid="mock-i18n-provider">{children}</div>
);

const MockSocketProvider = ({ children }: { children: React.ReactNode }) => (
  <div data-testid="mock-socket-provider">{children}</div>
);

const MockThemeProvider = ({ children }: { children: React.ReactNode }) => (
  <div data-testid="mock-theme-provider">{children}</div>
);

export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

export function AllTheProviders({
  children,
  user = defaultUser,
}: {
  children: React.ReactNode;
  user?: User;
}) {
  const queryClient = createTestQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <MockI18nProvider>
          <MockThemeProvider>
            <MockAuthProvider value={{ user, isAuthenticated: !!user, isLoading: false }}>
              <MockSocketProvider>{children}</MockSocketProvider>
            </MockAuthProvider>
          </MockThemeProvider>
        </MockI18nProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export function renderWithProviders(
  ui: ReactElement,
  {
    user = defaultUser,
    initialRoute = '/',
    ...options
  }: CustomRenderOptions = {}
) {
  if (initialRoute !== '/') {
    window.history.pushState({}, 'Test page', initialRoute);
  }

  return {
    ...render(ui, {
      wrapper: ({ children }) => (
        <AllTheProviders user={user}>{children}</AllTheProviders>
      ),
      ...options,
    }),
    user,
  };
}

// Re-export everything
export * from '@testing-library/react';
export { renderWithProviders as render };
