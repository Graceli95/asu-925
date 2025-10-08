'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

// Create AuthContext
const AuthContext = createContext();

// AuthProvider component
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  /**
   * Check if user is authenticated
   */
  const checkAuthStatus = async () => {
    try {
      setLoading(true);
      const userData = await authService.getCurrentUser();
      setUser(userData);
      setError(null);
    } catch (error) {
      setUser(null);
      setError(null); // Don't set error for auth check failures
    } finally {
      setLoading(false);
    }
  };

  /**
   * Login user
   * @param {Object} credentials - Login credentials
   */
  const login = async (credentials) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('AuthContext: Starting login process');
      const tokenData = await authService.login(credentials);
      console.log('AuthContext: Login successful, token data:', tokenData);
      
      // Get user data after successful login
      console.log('AuthContext: Fetching current user data...');
      const userData = await authService.getCurrentUser();
      console.log('AuthContext: User data fetched:', userData);
      setUser(userData);
      
      return tokenData;
    } catch (error) {
      console.error('AuthContext: Login error:', error);
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Register user
   * @param {Object} userData - User registration data
   */
  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      
      const newUser = await authService.register(userData);
      
      // Auto-login after successful registration
      await login({
        username: userData.username,
        password: userData.password
      });
      
      return newUser;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Logout user
   */
  const logout = async () => {
    try {
      setLoading(true);
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setError(null);
      setLoading(false);
    }
  };

  /**
   * Clear error
   */
  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    clearError,
    isAuthenticated: !!user,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use AuthContext
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
