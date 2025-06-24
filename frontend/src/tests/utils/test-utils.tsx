import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { I18nProvider } from '@/contexts/I18nContext'
import { SocketProvider } from '@/contexts/SocketContext'
import { User } from '@/types/user'

// Create a custom render function that includes all providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  user?: Partial<User>
  initialRoute?: string
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
}

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
  })
}

export function AllTheProviders({ 
  children,
  user = defaultUser,
}: { 
  children: React.ReactNode
  user?: User
}) {
  const queryClient = createTestQueryClient()

  // Mock AuthProvider with test user
  const MockAuthProvider = ({ children }: { children: React.ReactNode }) => {
    const value = {
      user,
      isAuthenticated: !!user,
      isLoading: false,
      login: async () => {},
      logout: async () => {},
      register: async () => {},
      updateProfile: async () => {},
    }

    return <AuthProvider value={value}>{children}</AuthProvider>
  }

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <I18nProvider>
          <ThemeProvider>
            <MockAuthProvider>
              <SocketProvider>
                {children}
              </SocketProvider>
            </MockAuthProvider>
          </ThemeProvider>
        </I18nProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
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
    window.history.pushState({}, 'Test page', initialRoute)
  }

  return {
    ...render(ui, {
      wrapper: ({ children }) => (
        <AllTheProviders user={user}>{children}</AllTheProviders>
      ),
      ...options,
    }),
    user,
  }
}

// Re-export everything
export * from '@testing-library/react'
export { renderWithProviders as render }