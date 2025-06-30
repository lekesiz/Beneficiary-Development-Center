import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export const UserRoleDebug: React.FC = () => {
  const { user } = useAuth();

  if (!user || process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <Card className="fixed bottom-4 right-4 w-80 z-50 bg-black/90 text-white border-yellow-500">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm text-yellow-400">🐛 User Role Debug</CardTitle>
      </CardHeader>
      <CardContent className="text-xs space-y-1">
        <div><strong>Email:</strong> {user.email}</div>
        <div><strong>Primary Role:</strong> {user.primaryRole || 'undefined'}</div>
        <div><strong>Role (legacy):</strong> {user.role || 'undefined'}</div>
        <div><strong>Roles Array:</strong></div>
        <div className="pl-2">
          {user.roles && user.roles.length > 0 ? (
            user.roles.map((role, index) => (
              <div key={index}>• {role.name} (id: {role.id})</div>
            ))
          ) : (
            <div className="text-red-400">Empty or undefined</div>
          )}
        </div>
        <div><strong>Tenant ID:</strong> {user.tenantId}</div>
        <div className="pt-2 text-yellow-400">
          <strong>Permission Checks:</strong>
        </div>
        <div className="pl-2">
          <div>
            Can Edit Program: {user.roles?.some(role => ['admin', 'manager', 'trainer'].includes(role.name)) || 
                              user.primaryRole && ['admin', 'manager', 'trainer'].includes(user.primaryRole) ? '✅' : '❌'}
          </div>
          <div>
            Can Set Status: {user.roles?.some(role => ['admin', 'manager'].includes(role.name)) || 
                            user.primaryRole && ['admin', 'manager'].includes(user.primaryRole) ? '✅' : '❌'}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};