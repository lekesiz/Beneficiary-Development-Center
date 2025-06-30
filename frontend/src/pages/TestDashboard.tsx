import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Shield, 
  Wifi, 
  Database, 
  Layout, 
  Key, 
  CheckCircle, 
  XCircle,
  Clock,
  Activity,
  Users,
  MessageSquare,
  Settings
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useSocket } from '@/contexts/SocketContext';

export default function TestDashboard() {
  const { user, isAuthenticated } = useAuth();
  const { isConnected } = useSocket();

  const systemStatus = [
    { label: 'Authentication', status: isAuthenticated, icon: Key },
    { label: 'Backend API', status: true, icon: Database },
    { label: 'WebSocket', status: isConnected, icon: Wifi },
    { label: 'Frontend', status: true, icon: Layout },
  ];

  const testPages = [
    {
      title: 'Authentication Test',
      description: 'Test login, logout, and token management',
      path: '/test-auth',
      icon: Key,
      color: 'bg-blue-500',
    },
    {
      title: 'Role Access Test',
      description: 'Test role-based permissions and access control',
      path: '/test-roles',
      icon: Shield,
      color: 'bg-purple-500',
    },
    {
      title: 'Real-time Test',
      description: 'Test Socket.IO and real-time features',
      path: '/test-realtime',
      icon: Wifi,
      color: 'bg-green-500',
    },
  ];

  const mainPages = [
    { title: 'Dashboard', path: '/dashboard', icon: Activity },
    { title: 'Beneficiaries', path: '/beneficiaries', icon: Users },
    { title: 'Programs', path: '/programs', icon: Layout },
    { title: 'Evaluations', path: '/evaluations', icon: CheckCircle },
    { title: 'Chat', path: '/chat', icon: MessageSquare },
    { title: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">BDC Platform Test Center</h1>
          <p className="text-gray-600 mt-2">Development and testing dashboard for the Beneficiary Development Center</p>
        </div>

        {/* System Status */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {systemStatus.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="flex items-center p-4 border rounded-lg">
                  <Icon className={`h-6 w-6 mr-3 ${item.status ? 'text-green-600' : 'text-red-600'}`} />
                  <div>
                    <p className="text-sm text-gray-600">{item.label}</p>
                    <p className={`font-medium ${item.status ? 'text-green-600' : 'text-red-600'}`}>
                      {item.status ? 'Online' : 'Offline'}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* User Info */}
        {user && (
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-xl font-semibold mb-4">Current User</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium">{user.email}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">Name</p>
                <p className="font-medium">{user.fullName}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">Role</p>
                <p className="font-medium capitalize">{user.primaryRole}</p>
              </div>
            </div>
          </div>
        )}

        {/* Test Pages */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Test Pages</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testPages.map((page) => {
              const Icon = page.icon;
              return (
                <Link
                  key={page.path}
                  to={page.path}
                  className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
                >
                  <div className={`inline-flex p-3 rounded-lg ${page.color} mb-4`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{page.title}</h3>
                  <p className="text-gray-600">{page.description}</p>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Main Application Pages */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Application Pages</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {mainPages.map((page) => {
              const Icon = page.icon;
              return (
                <Link
                  key={page.path}
                  to={page.path}
                  className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow text-center"
                >
                  <Icon className="h-8 w-8 mx-auto mb-2 text-gray-600" />
                  <p className="text-sm font-medium">{page.title}</p>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Quick Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Test Credentials</h3>
            <div className="space-y-2 text-sm">
              <p className="text-blue-800">
                <span className="font-medium">Admin:</span> admin@bdc.local / admin123
              </p>
              <p className="text-blue-800">
                <span className="font-medium">Trainer:</span> trainer@bdc.local / trainer123
              </p>
              <p className="text-blue-800">
                <span className="font-medium">Student:</span> student@bdc.local / student123
              </p>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-green-900 mb-2">Development Info</h3>
            <div className="space-y-2 text-sm">
              <p className="text-green-800">
                <span className="font-medium">Backend:</span> http://localhost:5001
              </p>
              <p className="text-green-800">
                <span className="font-medium">Frontend:</span> http://localhost:3000
              </p>
              <p className="text-green-800">
                <span className="font-medium">API Base:</span> /api/v1
              </p>
            </div>
          </div>
        </div>

        {/* Development Notice */}
        <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <Clock className="h-5 w-5 text-yellow-600 mr-3 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-yellow-900">Development Mode</h3>
              <p className="text-sm text-yellow-800 mt-1">
                This test dashboard is for development purposes only. Some features may have limited functionality
                while API endpoints and database connections are being configured.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}