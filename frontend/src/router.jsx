import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Simulator from './pages/Simulator';
import Analytics from './pages/Analytics';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';

export default function AppRouter() {
  return (
    <Routes>
      {/* Public Guest Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected Private Routes */}
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/simulator/:id" 
        element={
          <ProtectedRoute>
            <Simulator />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/analytics/:id" 
        element={
          <ProtectedRoute>
            <Analytics />
          </ProtectedRoute>
        } 
      />

      {/* Redirect Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
