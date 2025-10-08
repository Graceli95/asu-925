import axios from 'axios';
import { API_BASE_URL } from '../constants';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for HTTP-only cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging (optional)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors and token refresh
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 401/403 errors (unauthorized/forbidden)
    if ((error.response?.status === 401 || error.response?.status === 403) && !originalRequest._retry) {
      originalRequest._retry = true;

      // Don't try to refresh if we're already on login/register pages
      if (typeof window !== 'undefined') {
        const currentPath = window.location.pathname;
        if (currentPath === '/login' || currentPath === '/register') {
          console.log('Already on auth page, not attempting token refresh');
          return Promise.reject(error);
        }
      }

      try {
        console.log('Attempting token refresh...');
        // Attempt to refresh token - the refresh token will be sent via HTTP-only cookies
        await apiClient.post('/auth/refresh');
        
        console.log('Token refresh successful, retrying original request');
        // Retry the original request
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        console.error('Token refresh failed:', refreshError);
        
        // Only redirect if we're not already on login page
        if (typeof window !== 'undefined') {
          const currentPath = window.location.pathname;
          if (currentPath !== '/login') {
            console.log('Redirecting to login page');
            window.location.href = '/login';
          }
        }
        
        return Promise.reject(refreshError);
      }
    }

    // Handle other errors
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;
