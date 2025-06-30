import {
  Users,
  BookOpen,
  GraduationCap,
  ClipboardCheck,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  Home,
  Target,
  MessageSquare,
  Calendar,
  FileText,
} from 'lucide-react';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';

import { Breadcrumbs } from '@/components/common/Breadcrumbs';
import { useAuth } from '@/contexts/AuthContext';
import { hasAnyRole, ROLES, getHighestRole, getRoleDisplayName } from '@/utils/permissions';

const DashboardLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Define navigation items with role-based access control
  const allNavigationItems = [
    {
      name: t('navigation.dashboard'),
      href: '/dashboard',
      icon: Home,
      requiredRoles: [], // Accessible to all authenticated users
    },
    {
      name: t('navigation.beneficiaries'),
      href: '/beneficiaries',
      icon: Users,
      requiredRoles: [ROLES.ADMIN, ROLES.TRAINER],
    },
    {
      name: t('navigation.programs'),
      href: '/programs',
      icon: BookOpen,
      requiredRoles: [ROLES.ADMIN, ROLES.TRAINER],
    },
    {
      name: t('navigation.courses'),
      href: '/courses',
      icon: GraduationCap,
      requiredRoles: [ROLES.ADMIN, ROLES.TRAINER],
    },
    {
      name: t('navigation.sessions'),
      href: '/sessions',
      icon: Calendar,
      requiredRoles: [], // Accessible to all authenticated users
    },
    {
      name: 'Coach Notes',
      href: '/coach-notes',
      icon: FileText,
      requiredRoles: [ROLES.ADMIN, ROLES.TRAINER],
    },
    {
      name: t('navigation.evaluations'),
      href: '/evaluations',
      icon: ClipboardCheck,
      requiredRoles: [ROLES.ADMIN, ROLES.TRAINER, ROLES.STUDENT],
    },
    {
      name: t('navigation.learningPaths'),
      href: '/learning-paths',
      icon: Target,
      requiredRoles: [ROLES.ADMIN, ROLES.TRAINER, ROLES.STUDENT],
    },
    {
      name: 'Bilan de Compétence',
      href: '/bilan',
      icon: GraduationCap,
      requiredRoles: [], // Accessible to all authenticated users
    },
    {
      name: t('navigation.chat'),
      href: '/chat',
      icon: MessageSquare,
      requiredRoles: [], // Accessible to all authenticated users
    },
    {
      name: t('navigation.reports'),
      href: '/reports',
      icon: BarChart3,
      requiredRoles: [ROLES.ADMIN, ROLES.TRAINER, ROLES.STUDENT],
    },
    {
      name: t('navigation.settings'),
      href: '/settings',
      icon: Settings,
      requiredRoles: [], // Accessible to all authenticated users
    },
  ];

  // Filter navigation based on user roles using centralized permission system
  const hasRequiredRole = (requiredRoles: string[]) => {
    if (requiredRoles.length === 0) return true; // No restrictions
    return hasAnyRole(user, requiredRoles as any);
  };

  const navigation = allNavigationItems.filter((item) => hasRequiredRole(item.requiredRoles));

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      <div
        className={`fixed inset-0 z-40 bg-gray-600 bg-opacity-75 transition-opacity lg:hidden ${
          sidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform lg:translate-x-0 lg:static lg:inset-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-4 border-b">
            <h2 className="text-lg font-semibold">BDC Platform</h2>
            <button onClick={() => setSidebarOpen(false)} className="lg:hidden">
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`
                }
              >
                <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                {item.name}
              </NavLink>
            ))}
          </nav>

          {/* User section */}
          <div className="border-t p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
                  {user?.first_name?.[0]?.toUpperCase()}
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-gray-500">{getRoleDisplayName(getHighestRole(user) || ROLES.STUDENT)}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="mt-3 flex w-full items-center px-2 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-50"
            >
              <LogOut className="mr-3 h-5 w-5" />
              {t('navigation.logout')}
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 flex-col">
        {/* Top bar */}
        <header className="bg-white shadow-sm">
          <div className="flex h-16 items-center justify-between px-4">
            <button onClick={() => setSidebarOpen(true)} className="lg:hidden">
              <Menu className="h-6 w-6" />
            </button>
            <div className="flex-1" />
            {/* Additional header content can go here */}
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
          {/* Breadcrumbs */}
          <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-6 lg:px-8 py-3">
            <Breadcrumbs />
          </div>

          <div className="p-4 sm:p-6 lg:p-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
