import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import * as matchers from '@testing-library/jest-dom/matchers';
import { cleanup, render } from '@testing-library/react';
import React, { ReactElement } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { expect, afterEach, beforeAll, afterAll, vi } from 'vitest';

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

// Mock translations for tests
const testTranslations: Record<string, string> = {
  // Programs
  'programs.form.newProgram': 'Yeni Program',
  'programs.form.editProgram': 'Program Düzenle',
  'programs.form.createDescription': 'Yeni bir program oluşturun',
  'programs.form.updateDescription': 'Program bilgilerini güncelleyin',
  'programs.form.sections.basicInfo': 'Temel Bilgiler',
  'programs.form.sections.datesCapacity': 'Tarihler ve Kapasite',
  'programs.form.sections.locationFormat': 'Konum ve Format',
  'programs.form.sections.pricing': 'Ücretlendirme',
  'programs.form.sections.objectives': 'Program Hedefleri',
  'programs.form.sections.tags': 'Etiketler',
  'programs.form.fields.title': 'Program Adı',
  'programs.form.fields.code': 'Program Kodu',
  'programs.form.fields.type': 'Program Tipi',
  'programs.form.fields.status': 'Durum',
  'programs.form.fields.description': 'Açıklama',
  'programs.form.fields.startDate': 'Başlangıç Tarihi',
  'programs.form.fields.endDate': 'Bitiş Tarihi',
  'programs.form.fields.enrollmentStart': 'Kayıt Başlangıcı',
  'programs.form.fields.enrollmentEnd': 'Kayıt Bitişi',
  'programs.form.fields.minParticipants': 'Min. Katılımcı',
  'programs.form.fields.maxParticipants': 'Maks. Katılımcı',
  'programs.form.fields.codePlaceholder': 'Örn: PROG_2024',
  'programs.form.fields.codeAutoGenerate': 'Otomatik oluşturulur',
  'programs.form.fields.objectivePlaceholder': 'Yeni hedef ekleyin',
  'programs.form.fields.addObjective': 'Yeni hedef ekleyin',
  'programs.form.fields.tagPlaceholder': 'Yeni etiket ekleyin',
  'programs.form.fields.addTag': 'Yeni etiket ekleyin',
  'programs.form.fields.location': 'Konum',
  'programs.form.fields.isOnline': 'Online Program',
  'programs.form.fields.isHybrid': 'Hibrit Program',
  'programs.form.fields.sessionLocation': 'Oturum Lokasyonu',
  'programs.form.fields.sessionFormat': 'Oturum Formatı',
  'programs.form.fields.sessionLink': 'Oturum Bağlantısı',
  'programs.form.fields.isPaid': 'Ücretli Program',
  'programs.form.fields.price': 'Ücret',
  'programs.form.fields.currency': 'Para Birimi',
  'programs.form.sections.location': 'Konum ve Format',
  'programs.form.sections.dates': 'Tarihler ve Kapasite',
  'programs.form.messages.noPermission': 'Bu sayfaya erişim yetkiniz bulunmamaktadır.',
  'programs.form.messages.createSuccess': 'Program başarıyla oluşturuldu',
  'programs.form.messages.updateSuccess': 'Program başarıyla güncellendi',
  
  // Beneficiaries
  'beneficiaries.form.addNewBeneficiary': 'Add New Beneficiary',
  'beneficiaries.form.editBeneficiary': 'Edit Beneficiary',
  'beneficiaries.form.createDescription': 'Create a new beneficiary profile',
  'beneficiaries.form.updateDescription': 'Update beneficiary information',
  'beneficiaries.form.backToBeneficiaries': 'Back to Beneficiaries',
  'beneficiaries.form.title.create': 'Add New Beneficiary',
  'beneficiaries.form.title.edit': 'Edit Beneficiary',
  'beneficiaries.form.description.create': 'Create a new beneficiary profile',
  'beneficiaries.form.description.edit': 'Update beneficiary information',
  'beneficiaries.form.submit.create': 'Create Beneficiary',
  'beneficiaries.form.submit.update': 'Update Beneficiary',
  'beneficiaries.form.fields.firstName': 'First Name',
  'beneficiaries.form.fields.lastName': 'Last Name',
  'beneficiaries.form.fields.email': 'Email',
  'beneficiaries.form.fields.phone': 'Phone',
  'beneficiaries.form.fields.mobilePhone': 'Mobile Phone',
  'beneficiaries.form.fields.externalId': 'External ID',
  'beneficiaries.form.fields.status': 'Status',
  'beneficiaries.form.fields.tags': 'Tags',
  'beneficiaries.form.fields.tagPlaceholder': 'Add tags...',
  'beneficiaries.form.fields.tagInputPlaceholder': 'Add tag...',
  'beneficiaries.form.fields.addTag': 'Add tag...',
  'beneficiaries.form.fields.addCertification': 'Add certification...',
  'beneficiaries.form.fields.addSkill': 'Add skill...',
  'beneficiaries.form.fields.addInterest': 'Add interest...',
  'beneficiaries.form.fields.addGoal': 'Add goal...',
  'beneficiaries.form.fields.certifications': 'Certifications',
  'beneficiaries.form.fields.skills': 'Skills',
  'beneficiaries.form.fields.interests': 'Interests',
  'beneficiaries.form.fields.goals': 'Goals',
  'beneficiaries.form.placeholders.firstName': 'John',
  'beneficiaries.form.placeholders.lastName': 'Doe',
  'beneficiaries.form.placeholders.email': 'john.doe@example.com',
  'beneficiaries.form.placeholders.phone': '+1234567890',
  'beneficiaries.form.placeholders.mobilePhone': '+1234567890',
  'beneficiaries.form.placeholders.externalId': 'EXT-001',
  'beneficiaries.form.sections.basicInfo': 'Basic Information',
  'beneficiaries.form.sections.personalInfo': 'Personal Information',
  'beneficiaries.form.validation.firstNameMin': 'First name must be at least 2 characters',
  'beneficiaries.form.validation.lastNameMin': 'Last name must be at least 2 characters',
  'beneficiaries.form.validation.emailInvalid': 'Invalid email address',
  'beneficiaries.form.validation.phoneInvalid': 'Invalid phone number',
  
  // Settings
  'settings.title': 'Settings',
  'settings.description': 'Manage your account settings and preferences',
  'settings.tabs.profile': 'Profile',
  'settings.tabs.notifications': 'Notifications',
  'settings.tabs.security': 'Security',
  'settings.tabs.appearance': 'Appearance',
  'settings.profile.title': 'Profile Settings',
  'settings.profile.description': 'Update your personal information',
  'settings.notifications.title': 'Notification Preferences',
  'settings.notifications.description': 'Manage how you receive notifications',
  'settings.security.title': 'Security Settings',
  'settings.security.description': 'Manage your account security',
  'settings.appearance.title': 'Appearance Settings',
  'settings.appearance.description': 'Customize your interface',
  
  // Navigation
  'navigation.dashboard': 'Dashboard',
  'navigation.beneficiaries': 'Beneficiaries',
  'navigation.programs': 'Programs',
  'navigation.courses': 'Courses',
  'navigation.evaluations': 'Evaluations',
  'navigation.learningPaths': 'Learning Paths',
  'navigation.reports': 'Reports',
  'navigation.settings': 'Settings',
  
  // Common
  'common.backTo': 'Geri',
  'common.save': 'Kaydet',
  'common.cancel': 'İptal',
  'common.delete': 'Sil',
  'common.edit': 'Düzenle',
  'common.create': 'Oluştur',
  'common.loading': 'Yükleniyor...',
  'common.search': 'Search',
  'common.logout': 'Logout',
};

vi.mock('@/contexts/I18nContext', () => ({
  I18nProvider: ({ children }: { children: React.ReactNode }) => children,
  useI18n: () => ({ t: (key: string) => testTranslations[key] || key }),
}));

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => testTranslations[key] || key,
    i18n: {
      language: 'tr',
      changeLanguage: vi.fn(),
    },
  }),
  Trans: ({ children }: { children: React.ReactNode }) => children,
  initReactI18next: {
    type: '3rdParty',
    init: vi.fn(),
  },
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
