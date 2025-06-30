import {
  Users,
  BookOpen,
  TrendingUp,
  Calendar,
  Settings,
  LogOut,
  Menu,
  X,
  Home,
} from 'lucide-react';
import * as React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';

import NotificationCenter from '@/components/coach/NotificationCenter';
import { useAuth } from '@/contexts/AuthContext';

export default function CoachLayout() {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/coach/dashboard', icon: Home },
    { name: 'Öğrencilerim', href: '/coach/students', icon: Users },
    { name: 'Programlar', href: '/coach/programs', icon: BookOpen },
    { name: 'Raporlar', href: '/coach/reports', icon: TrendingUp },
    { name: 'Takvim', href: '/coach/calendar', icon: Calendar },
    { name: 'Ayarlar', href: '/coach/settings', icon: Settings },
  ];

  const isActive = (path: string) => location.pathname.startsWith(path);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 fixed w-full top-0 z-40">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="p-2 rounded-md text-gray-400 lg:hidden"
              >
                {isSidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
              <h1 className="ml-2 text-xl font-semibold text-gray-900">BDC Koç Paneli</h1>
            </div>

            <div className="flex items-center space-x-4">
              {/* Notification Center */}
              <NotificationCenter />

              {/* User Menu */}
              <div className="flex items-center">
                <div className="mr-3 text-right">
                  <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                  <p className="text-xs text-gray-500">{user?.role}</p>
                </div>
                <button
                  onClick={logout}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                  title="Çıkış Yap"
                >
                  <LogOut className="h-5 w-5 text-gray-600" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-screen pt-16">
        {/* Sidebar */}
        <aside
          className={`${
            isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } fixed inset-y-0 left-0 z-30 w-64 bg-gray-900 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
        >
          <div className="flex flex-col h-full pt-5 pb-4 overflow-y-auto">
            <nav className="mt-5 flex-1 px-2 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`${
                      isActive(item.href)
                        ? 'bg-gray-800 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    } group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors`}
                    onClick={() => setIsSidebarOpen(false)}
                  >
                    <Icon
                      className={`${
                        isActive(item.href) ? 'text-white' : 'text-gray-400 group-hover:text-white'
                      } mr-3 flex-shrink-0 h-6 w-6`}
                    />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <Outlet />
            </div>
          </div>
        </main>
      </div>

      {/* Mobile sidebar backdrop */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </div>
  );
}
