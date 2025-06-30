import React, { useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

const AuthDebug: React.FC = () => {
  const auth = useAuth();

  useEffect(() => {
    console.log('AuthDebug - Current auth state:', {
      user: auth.user,
      isAuthenticated: auth.isAuthenticated,
      isLoading: auth.isLoading,
      accessToken: localStorage.getItem('access_token'),
      refreshToken: localStorage.getItem('refresh_token'),
      tenantId: localStorage.getItem('tenant_id'),
    });
  }, [auth]);

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: 20,
      right: 20,
      background: 'rgba(0,0,0,0.8)',
      color: 'white',
      padding: '10px',
      borderRadius: '5px',
      fontSize: '12px',
      maxWidth: '300px',
      zIndex: 9999,
    }}>
      <h4 style={{ margin: '0 0 10px 0' }}>Auth Debug</h4>
      <div>User: {auth.user ? auth.user.email : 'null'}</div>
      <div>Authenticated: {auth.isAuthenticated ? 'true' : 'false'}</div>
      <div>Loading: {auth.isLoading ? 'true' : 'false'}</div>
      <div>Token: {localStorage.getItem('access_token') ? 'Present' : 'Missing'}</div>
    </div>
  );
};

export default AuthDebug;