import { useAuth } from '@/contexts/AuthContext';
import { Users, BookOpen, ClipboardCheck, TrendingUp, Activity, Calendar, Award, Target } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function SimpleDashboard() {
  const { user } = useAuth();

  const stats = [
    { label: 'Total Beneficiaries', value: '0', icon: Users, color: 'text-blue-600' },
    { label: 'Active Programs', value: '0', icon: BookOpen, color: 'text-green-600' },
    { label: 'Evaluations', value: '0', icon: ClipboardCheck, color: 'text-purple-600' },
    { label: 'Success Rate', value: '0%', icon: TrendingUp, color: 'text-orange-600' },
  ];

  const quickActions = [
    { label: 'Add Beneficiary', path: '/beneficiaries/new', icon: Users },
    { label: 'Create Program', path: '/programs/new', icon: BookOpen },
    { label: 'Schedule Evaluation', path: '/evaluations', icon: ClipboardCheck },
    { label: 'View Reports', path: '/reports', icon: Activity },
  ];

  const recentActivities = [
    { action: 'System initialized', time: 'Just now', icon: Activity },
    { action: 'User logged in', time: '1 minute ago', icon: Users },
    { action: 'Dashboard loaded', time: 'Just now', icon: Target },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user?.firstName || 'User'}!</h1>
        <p className="text-gray-600 mt-2">Here's an overview of your Beneficiary Development Center</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <Icon className={`h-8 w-8 ${stat.color}`} />
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-2 gap-4">
              {quickActions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <Link
                    key={index}
                    to={action.path}
                    className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-colors"
                  >
                    <Icon className="h-5 w-5 text-gray-600 mr-3" />
                    <span className="font-medium text-gray-900">{action.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>

          {/* User Info */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Profile</h2>
            <div className="space-y-3">
              <div className="flex items-center">
                <Award className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-gray-600">Role:</span>
                <span className="ml-2 font-medium text-gray-900 capitalize">{user?.primaryRole || 'Unknown'}</span>
              </div>
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-gray-600">Member since:</span>
                <span className="ml-2 font-medium text-gray-900">
                  {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown'}
                </span>
              </div>
              <div className="flex items-center">
                <Target className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-gray-600">Status:</span>
                <span className="ml-2">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivities.map((activity, index) => {
              const Icon = activity.icon;
              return (
                <div key={index} className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-8 w-8 rounded-full bg-gray-100">
                      <Icon className="h-4 w-4 text-gray-600" />
                    </div>
                  </div>
                  <div className="ml-3 flex-1">
                    <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Development Notice */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Activity className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Development Mode</h3>
            <p className="mt-1 text-sm text-blue-700">
              This is a simplified dashboard for testing. API integration will be enabled once backend services are fully configured.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}