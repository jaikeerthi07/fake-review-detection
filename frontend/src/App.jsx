import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Preview from './pages/Preview';
import Training from './pages/Training';
import MethodSelect from './pages/MethodSelect';
import SingleReview from './pages/SingleReview';
import UrlAnalysis from './pages/UrlAnalysis';
import Login from './pages/Login';
import Register from './pages/Register';
import PerformanceAnalysis from './pages/PerformanceAnalysis';
import Charts from './pages/Charts';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {

  return (
    <Router>
      <div className="min-h-screen bg-slate-50 font-sans">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Routes */}
            <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
            <Route path="/preview" element={<ProtectedRoute><Preview /></ProtectedRoute>} />
            <Route path="/training" element={<ProtectedRoute><Training /></ProtectedRoute>} />
            <Route path="/select-method" element={<ProtectedRoute><MethodSelect /></ProtectedRoute>} />
            <Route path="/analyze/single" element={<ProtectedRoute><SingleReview /></ProtectedRoute>} />
            <Route path="/analyze/url" element={<ProtectedRoute><UrlAnalysis /></ProtectedRoute>} />
            <Route path="/performance" element={<ProtectedRoute><PerformanceAnalysis /></ProtectedRoute>} />
            <Route path="/charts" element={<ProtectedRoute><Charts /></ProtectedRoute>} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
