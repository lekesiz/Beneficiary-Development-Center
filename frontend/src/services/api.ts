import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api/v1';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token and tenant ID
api.interceptors.request.use(
  (config) => {
    // Add auth token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add tenant ID
    const tenantId = localStorage.getItem('tenant_id') || '1';
    config.headers['X-Tenant-ID'] = tenantId;

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and errors
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export { api };

// Convenience methods
export const apiGet = (url: string, config?: AxiosRequestConfig) => api.get(url, config);
export const apiPost = (url: string, data?: any, config?: AxiosRequestConfig) => api.post(url, data, config);
export const apiPut = (url: string, data?: any, config?: AxiosRequestConfig) => api.put(url, data, config);
export const apiPatch = (url: string, data?: any, config?: AxiosRequestConfig) => api.patch(url, data, config);
export const apiDelete = (url: string, config?: AxiosRequestConfig) => api.delete(url, config);

export default api;