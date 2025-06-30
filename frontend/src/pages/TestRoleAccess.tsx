import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Shield, User, UserCheck, Users } from 'lucide-react';

export default function TestRoleAccess() {
  const { user, login, logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string, type: 'info' | 'success' | 'error' = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    setLogs(prev => [...prev, `[${timestamp}] ${prefix} ${message}`]);
  };

  const testUsers = [
    { email: 'admin@bdc.local', password: 'admin123', role: 'admin', icon: Shield, color: 'text-red-600' },
    { email: 'trainer@bdc.local', password: 'trainer123', role: 'trainer', icon: UserCheck, color: 'text-blue-600' },
    { email: 'student@bdc.local', password: 'student123', role: 'student', icon: User, color: 'text-green-600' },
  ];

  const loginAs = async (email: string, password: string, expectedRole: string) => {
    setLoading(true);
    addLog(`Attempting to login as ${expectedRole}...`);
    
    try {
      await login(email, password, 1);
      addLog(`Successfully logged in as ${email}`, 'success');
      
      // Check role
      setTimeout(() => {
        if (user?.primaryRole === expectedRole) {
          addLog(`Role verified: ${expectedRole}`, 'success');
        } else {
          addLog(`Role mismatch! Expected: ${expectedRole}, Got: ${user?.primaryRole}`, 'error');
        }
      }, 1000);
    } catch (error: any) {
      addLog(`Login failed: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const testAccessControl = () => {
    if (!user) {
      addLog('No user logged in', 'error');
      return;
    }

    addLog(`Testing access control for role: ${user.primaryRole}`);
    
    // Test role-based permissions
    const permissions = {
      admin: ['view_all_users', 'manage_programs', 'manage_evaluations', 'view_reports', 'system_settings'],
      trainer: ['view_assigned_students', 'manage_courses', 'create_evaluations', 'view_reports'],
      student: ['view_own_profile', 'take_evaluations', 'view_own_progress'],
    };

    const userPermissions = permissions[user.primaryRole as keyof typeof permissions] || [];
    
    addLog(`Permissions for ${user.primaryRole}:`);
    userPermissions.forEach(perm => {
      addLog(`  • ${perm}`, 'success');
    });

    // Test restricted access
    const restrictedActions = {
      admin: [],
      trainer: ['system_settings', 'manage_all_users'],
      student: ['manage_programs', 'create_evaluations', 'view_other_users'],
    };

    const restricted = restrictedActions[user.primaryRole as keyof typeof restrictedActions] || [];
    if (restricted.length > 0) {
      addLog(`Restricted actions for ${user.primaryRole}:`);
      restricted.forEach(action => {
        addLog(`  ❌ ${action}`, 'error');
      });
    }
  };

  const handleLogout = async () => {
    addLog('Logging out...');
    await logout();
    addLog('Logged out successfully', 'success');
    setLogs([]);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Role-Based Access Control Test</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Test Users */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Test Users</h2>
            <div className="space-y-3">
              {testUsers.map((testUser) => {
                const Icon = testUser.icon;
                const isCurrentUser = user?.email === testUser.email;
                
                return (
                  <div
                    key={testUser.email}
                    className={`p-4 border rounded-lg ${isCurrentUser ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Icon className={`h-6 w-6 ${testUser.color} mr-3`} />
                        <div>
                          <p className="font-medium">{testUser.role.toUpperCase()}</p>
                          <p className="text-sm text-gray-600">{testUser.email}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => loginAs(testUser.email, testUser.password, testUser.role)}
                        disabled={loading || isCurrentUser}
                        className={`px-4 py-2 rounded ${
                          isCurrentUser
                            ? 'bg-gray-300 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                        }`}
                      >
                        {isCurrentUser ? 'Current' : 'Login'}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Current User Info */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Current User</h2>
            {user ? (
              <div className="space-y-3">
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
                <div className="flex gap-3">
                  <button
                    onClick={testAccessControl}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded"
                  >
                    Test Permissions
                  </button>
                  <button
                    onClick={handleLogout}
                    className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded"
                  >
                    Logout
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No user logged in</p>
            )}
          </div>
        </div>

        {/* Console Output */}
        <div className="mt-6 bg-black text-green-400 p-6 rounded-lg font-mono text-sm">
          <h3 className="text-white mb-3">Console Output:</h3>
          <div className="space-y-1 max-h-96 overflow-y-auto">
            {logs.length > 0 ? (
              logs.map((log, index) => (
                <div key={index}>{log}</div>
              ))
            ) : (
              <div className="text-gray-500">No logs yet. Try logging in as different users.</div>
            )}
          </div>
        </div>

        {/* Role Information */}
        <div className="mt-6 bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Role Capabilities</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-red-200 rounded-lg">
              <h3 className="font-semibold text-red-600 mb-2">Admin</h3>
              <ul className="text-sm space-y-1">
                <li>• Full system access</li>
                <li>• Manage all users</li>
                <li>• Configure settings</li>
                <li>• View all reports</li>
              </ul>
            </div>
            <div className="p-4 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-600 mb-2">Trainer</h3>
              <ul className="text-sm space-y-1">
                <li>• Manage assigned students</li>
                <li>• Create courses</li>
                <li>• Grade evaluations</li>
                <li>• View student reports</li>
              </ul>
            </div>
            <div className="p-4 border border-green-200 rounded-lg">
              <h3 className="font-semibold text-green-600 mb-2">Student</h3>
              <ul className="text-sm space-y-1">
                <li>• View own profile</li>
                <li>• Take evaluations</li>
                <li>• Track progress</li>
                <li>• Access courses</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}