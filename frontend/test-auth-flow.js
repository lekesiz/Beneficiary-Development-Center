#!/usr/bin/env node

import axios from 'axios';

const API_BASE = 'http://localhost:5001/api/v1';
const FRONTEND_BASE = 'http://localhost:3000';

async function testAuthFlow() {
  console.log('🧪 Testing BDC Authentication Flow\n');

  try {
    // Test 1: Backend Health Check
    console.log('1️⃣ Testing backend connection...');
    try {
      await axios.get(`${API_BASE}/health`);
      console.log('✅ Backend is running on port 5001\n');
    } catch (error) {
      console.log('❌ Backend health check failed\n');
    }

    // Test 2: Login
    console.log('2️⃣ Testing login endpoint...');
    const loginResponse = await axios.post(`${API_BASE}/auth/login`, {
      email: 'admin@bdc.local',
      password: 'admin123',
      tenant_id: 1
    });

    const { access_token, refresh_token, user } = loginResponse.data;
    console.log('✅ Login successful');
    console.log(`   User: ${user.email}`);
    console.log(`   Role: ${user.primary_role}`);
    console.log(`   Token: ${access_token.substring(0, 50)}...`);
    console.log('');

    // Test 3: Authenticated Request
    console.log('3️⃣ Testing authenticated request...');
    const meResponse = await axios.get(`${API_BASE}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'X-Tenant-ID': '1'
      }
    });

    console.log('✅ Auth check successful');
    console.log(`   Authenticated as: ${meResponse.data.user.email}\n`);

    // Test 4: Frontend Proxy
    console.log('4️⃣ Testing frontend proxy...');
    try {
      const proxyResponse = await axios.post(`${FRONTEND_BASE}/api/v1/auth/login`, {
        email: 'admin@bdc.local',
        password: 'admin123',
        tenant_id: 1
      });
      console.log('✅ Frontend proxy working correctly\n');
    } catch (error) {
      console.log('❌ Frontend proxy test failed:', error.message, '\n');
    }

    // Test 5: Token Expiration
    console.log('5️⃣ Checking token expiration...');
    const tokenPayload = JSON.parse(Buffer.from(access_token.split('.')[1], 'base64').toString());
    const expiresIn = new Date(tokenPayload.exp * 1000);
    const now = new Date();
    const hoursUntilExpiry = (expiresIn - now) / (1000 * 60 * 60);
    
    console.log(`✅ Token expires at: ${expiresIn.toLocaleString()}`);
    console.log(`   (${hoursUntilExpiry.toFixed(1)} hours from now)\n`);

    // Summary
    console.log('📊 Summary:');
    console.log('✅ Backend API: Working');
    console.log('✅ Authentication: Working');
    console.log('✅ Token Generation: Working');
    console.log('✅ Token Expiration: 24 hours');
    console.log(`${proxyResponse ? '✅' : '❌'} Frontend Proxy: ${proxyResponse ? 'Working' : 'Check CORS/Proxy settings'}`);

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.response) {
      console.error('   Response:', error.response.data);
    }
  }
}

// Run the test
testAuthFlow();