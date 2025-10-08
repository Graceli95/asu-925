import apiClient from '../utils/apiClient';
import { API_ENDPOINTS } from '../constants';

/**
 * Authentication service for handling user authentication
 */
export const authService = {
  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} - User data
   */
  async register(userData) {
    try {
      console.log('Registering user with data:', userData);
      const response = await apiClient.post(API_ENDPOINTS.REGISTER, userData);
      console.log('Registration response:', response);
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      console.error('Error response:', error.response);
      console.error('Error status:', error.response?.status);
      console.error('Error data:', error.response?.data);
      
      // Handle CORS errors specifically
      if (error.code === 'ERR_NETWORK' || error.message.includes('CORS')) {
        throw new Error('Network error: Unable to connect to server. Please check if the backend is running.');
      }
      
      throw new Error(error.response?.data?.detail || error.message || 'Registration failed');
    }
  },

  /**
   * Login user
   * @param {Object} credentials - Login credentials
   * @returns {Promise<Object>} - Token data
   */
  async login(credentials) {
    try {
      console.log('AuthService: Attempting login with credentials:', { username: credentials.username });
      const response = await apiClient.post(API_ENDPOINTS.LOGIN, credentials);
      console.log('AuthService: Login response:', response);
      console.log('AuthService: Response cookies:', response.headers['set-cookie']);
      return response.data;
    } catch (error) {
      console.error('AuthService: Login error:', error);
      console.error('AuthService: Error response:', error.response);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  },

  /**
   * Logout user
   * @returns {Promise<Object>} - Logout confirmation
   */
  async logout() {
    try {
      const response = await apiClient.post(API_ENDPOINTS.LOGOUT);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Logout failed');
    }
  },

  /**
   * Refresh access token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} - New token data
   */
  async refreshToken(refreshToken) {
    try {
      const response = await apiClient.post(API_ENDPOINTS.REFRESH, {
        refresh_token: refreshToken
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Token refresh failed');
    }
  },

  /**
   * Get current user information
   * @returns {Promise<Object>} - Current user data
   */
  async getCurrentUser() {
    try {
      console.log('AuthService: Fetching current user...');
      const response = await apiClient.get(API_ENDPOINTS.ME);
      console.log('AuthService: getCurrentUser response:', response);
      return response.data;
    } catch (error) {
      console.error('AuthService: getCurrentUser error:', error);
      console.error('AuthService: Error response:', error.response);
      throw new Error(error.response?.data?.detail || 'Failed to get user info');
    }
  },

  /**
   * Check if user is authenticated
   * @returns {Promise<boolean>} - Authentication status
   */
  async isAuthenticated() {
    try {
      await this.getCurrentUser();
      return true;
    } catch (error) {
      return false;
    }
  }
};
