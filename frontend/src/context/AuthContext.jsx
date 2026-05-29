import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Create Auth Context
const AuthContext = createContext(null);

// Configure Axios Default Interceptor
// This interceptor automatically attaches the Bearer token to all outgoing API calls if present.
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize and check persistent token in localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('access_token');
    const storedEmail = localStorage.getItem('user_email');
    const storedId = localStorage.getItem('user_id');

    if (storedToken && storedEmail && storedId) {
      setUser({
        email: storedEmail,
        id: parseInt(storedId, 10),
      });
    }
    setLoading(false);
  }, []);

  // Configure response interceptor to auto-logout on 401 (expired/invalid token)
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && error.response.status === 401) {
          // Automatic system logout on token expiry
          logout();
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post('/api/auth/login', { email, password });
      const { access_token, user_id, email: userEmail } = response.data;

      // 1. Cache values inside localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user_email', userEmail);
      localStorage.setItem('user_id', user_id.toString());

      // 2. Update React auth states
      setUser({
        email: userEmail,
        id: user_id,
      });

      return { success: true };
    } catch (error) {
      console.error("Login attempt failed:", error);
      const message = error.response?.data?.detail || "Authentication server offline. Could not complete login.";
      return { success: false, error: message };
    }
  };

  const register = async (email, password) => {
    try {
      const response = await axios.post('/api/auth/register', { email, password });
      const { access_token, user_id, email: userEmail } = response.data;

      // 1. Cache values inside localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user_email', userEmail);
      localStorage.setItem('user_id', user_id.toString());

      // 2. Update React auth states
      setUser({
        email: userEmail,
        id: user_id,
      });

      return { success: true };
    } catch (error) {
      console.error("Registration attempt failed:", error);
      const message = error.response?.data?.detail || "Registration failed. Database offline or invalid formatting.";
      return { success: false, error: message };
    }
  };

  const logout = () => {
    // 1. Flush localStorage cached keys
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_id');

    // 2. Wipe React auth states
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

// Custom hook helper for utilizing auth features in components
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be executed within an AuthProvider wrapper.');
  }
  return context;
}
