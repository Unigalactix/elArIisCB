import { useState, useEffect, useCallback } from 'react';
import { User, AuthResponse } from '../types/chat';
import { apiService } from '../services/api';

interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  error: string | null;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  employee_id?: string;
  department?: string;
  position?: string;
}

export const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (apiService.isAuthenticated()) {
          const currentUser = apiService.getCurrentUser();
          if (currentUser) {
            setUser(currentUser);
          } else {
            // Token exists but no user data, fetch profile
            const profile = await apiService.getProfile();
            setUser(profile);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        // Clear invalid auth data
        await apiService.logout();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response: AuthResponse = await apiService.login(username, password);
      setUser(response.user);
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.non_field_errors?.[0] ||
                          'Login failed. Please check your credentials.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (userData: RegisterData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response: AuthResponse = await apiService.register(userData);
      setUser(response.user);
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.username?.[0] ||
                          error.response?.data?.email?.[0] ||
                          'Registration failed. Please try again.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await apiService.logout();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshProfile = useCallback(async () => {
    if (!apiService.isAuthenticated()) return;
    
    try {
      const profile = await apiService.getProfile();
      setUser(profile);
      localStorage.setItem('user', JSON.stringify(profile));
    } catch (error) {
      console.error('Profile refresh error:', error);
    }
  }, []);

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshProfile,
    error,
  };
};