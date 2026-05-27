import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Setup from './pages/Setup';
import InterviewRoom from './pages/InterviewRoom';
import PerformanceReport from './pages/PerformanceReport';
import AdminPanel from './pages/AdminPanel';

// Layout
import Navbar from './components/Layout/Navbar';
import Sidebar from './components/Layout/Sidebar';

// Protected Route shell wrapper
const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && user.role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  return children;
};

// Main App component wrapping subelements
const AppContent = () => {
  const { user } = useAuth();

  return (
    <Router>
      <Routes>
        {/* Auth paths */}
        <Route path="/login" element={!user ? <Login /> : <Navigate to="/" />} />
        <Route path="/register" element={!user ? <Register /> : <Navigate to="/" />} />

        {/* Protected Dashboard shell */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <div className="min-h-screen flex flex-col bg-cyber-950 text-slate-100 selection:bg-indigo-500/30 selection:text-slate-100">
                {/* Global shell Navbar */}
                <Navbar />
                
                <div className="flex flex-1 relative">
                  {/* Left Navigation Sidebar */}
                  <Sidebar />
                  
                  {/* Master center page display panel */}
                  <main className="flex-1 p-6 md:p-8 overflow-y-auto max-h-[calc(100vh-4rem)]">
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/setup" element={<Setup />} />
                      <Route path="/interview/:sessionId" element={<InterviewRoom />} />
                      <Route path="/report/:sessionId" element={<PerformanceReport />} />
                      
                      {/* Admin Route */}
                      <Route
                        path="/admin"
                        element={
                          <ProtectedRoute requireAdmin={true}>
                            <AdminPanel />
                          </ProtectedRoute>
                        }
                      />
                      
                      {/* Catch-all fallback */}
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
