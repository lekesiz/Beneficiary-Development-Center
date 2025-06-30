import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/api/client';

export default function TestAuth() {
  const auth = useAuth();
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  };

  const testLogin = async () => {
    addLog('Starting login test...');
    try {
      await auth.login('admin@bdc.local', 'admin123', 1);
      addLog('✅ Login successful!');
    } catch (error: any) {
      addLog(`❌ Login failed: ${error.message}`);
    }
  };

  const testAuthCheck = async () => {
    addLog('Checking auth status...');
    addLog(`isAuthenticated: ${auth.isAuthenticated}`);
    addLog(`isLoading: ${auth.isLoading}`);
    addLog(`user: ${auth.user?.email || 'null'}`);
    
    const token = localStorage.getItem('access_token');
    if (token) {
      addLog(`Token present: ${token.substring(0, 50)}...`);
      
      try {
        const response = await apiClient.get('/auth/me');
        addLog(`✅ Auth check successful: ${response.data.user.email}`);
      } catch (error: any) {
        addLog(`❌ Auth check failed: ${error.response?.data?.message || error.message}`);
      }
    } else {
      addLog('❌ No token in localStorage');
    }
  };

  const clearAuth = () => {
    localStorage.clear();
    window.location.reload();
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Authentication Test Page</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button onClick={testLogin} style={{ marginRight: '10px' }}>Test Login</button>
        <button onClick={testAuthCheck} style={{ marginRight: '10px' }}>Check Auth</button>
        <button onClick={clearAuth}>Clear & Reload</button>
      </div>

      <div style={{ backgroundColor: '#f0f0f0', padding: '10px', borderRadius: '5px' }}>
        <h3>Auth State:</h3>
        <div>isAuthenticated: {auth.isAuthenticated ? '✅' : '❌'}</div>
        <div>isLoading: {auth.isLoading ? '⏳' : '✅'}</div>
        <div>user: {auth.user?.email || 'null'}</div>
      </div>

      <div style={{ marginTop: '20px', backgroundColor: '#000', color: '#0f0', padding: '10px', borderRadius: '5px', minHeight: '200px' }}>
        <h3>Console:</h3>
        {logs.map((log, i) => (
          <div key={i}>{log}</div>
        ))}
      </div>
    </div>
  );
}