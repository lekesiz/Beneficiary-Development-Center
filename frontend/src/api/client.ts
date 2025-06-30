import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { toast } from 'react-hot-toast';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5001/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      
      // Debug logging
      console.log('[API Client] Request:', {
        url: config.url,
        method: config.method,
        hasToken: !!token,
        tokenPreview: token ? `${token.substring(0, 20)}...` : 'none'
      });
    }

    // Add tenant ID
    const tenantId = localStorage.getItem('tenant_id');
    if (tenantId) {
      config.headers['X-Tenant-ID'] = tenantId;
    }

    return config;
  },
  (error) => {
    console.error('[API Client] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & {
      _retry?: boolean;
    };

    console.error('[API Client] Response error:', {
      status: error.response?.status,
      url: error.config?.url,
      message: error.response?.data,
    });

    // Handle 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Don't retry for auth endpoints
      if (originalRequest.url?.includes('/auth/')) {
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      try {
        // Try to refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          console.log('[API Client] Attempting token refresh...');
          const response = await axios.post(
            `${apiClient.defaults.baseURL}/auth/refresh`,
            {},
            {
              headers: {
                Authorization: `Bearer ${refreshToken}`,
              },
            }
          );

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          console.log('[API Client] Token refreshed successfully');

          // Retry original request
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }

          return apiClient(originalRequest);
        } else {
          console.log('[API Client] No refresh token available');
        }
      } catch (refreshError) {
        console.error('[API Client] Token refresh failed:', refreshError);
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('tenant_id');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Handle other errors
    if (error.response) {
      const errorData = error.response.data as { message?: string };
      const message = errorData?.message || 'An error occurred';

      // Don't show toast for validation errors (handle them in forms)
      if (error.response.status !== 400) {
        toast.error(message);
      }
    } else if (error.request) {
      toast.error('Network error. Please check your connection.');
    } else {
      toast.error('An unexpected error occurred.');
    }

    return Promise.reject(error);
  }
);

export default apiClient;

// Helper functions
export const setAuthToken = (token: string) => {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

export const removeAuthToken = () => {
  delete apiClient.defaults.headers.common['Authorization'];
};

export const setTenantId = (tenantId: string) => {
  apiClient.defaults.headers.common['X-Tenant-ID'] = tenantId;
};

export const removeTenantId = () => {
  delete apiClient.defaults.headers.common['X-Tenant-ID'];
};
