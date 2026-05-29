import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { RefreshCw } from 'lucide-react';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-cyber-bg flex flex-col items-center justify-center space-y-4">
        <RefreshCw className="w-8 h-8 text-cyber-cyan animate-spin" />
        <p className="text-sm font-tech text-cyber-cyan tracking-widest uppercase">
          VERIFYING NEURAL ENCRYPTION CODES...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login page and store the original location for post-login return redirections
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
