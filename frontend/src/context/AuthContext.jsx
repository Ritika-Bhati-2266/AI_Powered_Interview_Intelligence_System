import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    const name = localStorage.getItem('name');
    
    if (savedToken && role) {
      setUser({ token: savedToken, role, name });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, role, full_name } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('role', role);
      localStorage.setItem('name', full_name || email);
      
      const loggedUser = { token: access_token, role, name: full_name || email };
      setUser(loggedUser);
      setToken(access_token);
      return loggedUser;
    } catch (error) {
      console.error("Login failure:", error);
      throw error.response?.data?.detail || "Invalid login credentials.";
    }
  };

  const register = async (email, password, fullName) => {
    try {
      await api.post('/auth/register', {
        email,
        password,
        full_name: fullName
      });
    } catch (error) {
      console.error("Registration failure:", error);
      throw error.response?.data?.detail || "Email is already registered.";
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('name');
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be utilized within an AuthProvider.');
  }
  return context;
};
