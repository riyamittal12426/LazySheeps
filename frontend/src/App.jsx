import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { SignIn, SignUp, useAuth as useClerkAuth } from '@clerk/clerk-react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import EnhancedDashboard from './pages/EnhancedDashboard';
import Repositories from './pages/Repositories';
import RepositoryDetail from './pages/RepositoryDetail';
import Contributors from './pages/Contributors';
import ContributorDetail from './pages/ContributorDetail';
import ContributorStats from './pages/ContributorStats';
import UserProfile from './pages/UserProfile';
import GitHubCallback from './pages/GitHubCallback';
import RepositorySelection from './pages/RepositorySelection';
import { ReactFlowProvider } from '@xyflow/react';

// Protected Route Component using Clerk or JWT
const ProtectedRoute = ({ children }) => {
  const { isLoaded, isSignedIn } = useClerkAuth();
  const jwtToken = localStorage.getItem('access_token');

  // Show loading state while Clerk is initializing
  if (!isLoaded && !jwtToken) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  // Check if authenticated via Clerk or JWT
  const isAuthenticated = isSignedIn || !!jwtToken;

  // Redirect to sign-in if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/sign-in" replace />;
  }

  // User is authenticated, show the protected content
  return children;
};

function AppRoutes() {
  return (
    <ReactFlowProvider>
      <Routes>
        {/* Clerk Auth Routes */}
        <Route path="/sign-in/*" element={
          <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
            <SignIn routing="path" path="/sign-in" />
          </div>
        } />
        <Route path="/sign-up/*" element={
          <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
            <SignUp routing="path" path="/sign-up" />
          </div>
        } />
        
        {/* GitHub OAuth Routes */}
        <Route path="/auth/github/callback" element={<GitHubCallback />} />
        
        {/* Onboarding Routes */}
        <Route path="/onboarding/repositories" element={
          <ProtectedRoute>
            <RepositorySelection />
          </ProtectedRoute>
        } />
        
        {/* Protected Routes */}
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          {/* Redirect root to dashboard */}
          <Route index element={<Navigate to="/dashboard" replace />} />
          
          {/* Dashboard Routes */}
          <Route path="dashboard" element={<Dashboard />} />
          
          {/* Enhanced Dashboard with Analytics */}
          <Route path="analytics" element={<EnhancedDashboard />} />
          
          {/* User Profile */}
          <Route path="profile" element={<UserProfile />} />

          {/* Repository Routes */}
          <Route path="repositories">
            <Route index element={<Repositories />} />
            <Route path=":repoId" element={<RepositoryDetail />} />
          </Route>

          {/* Contributor Routes */}
          <Route path="contributors">
            <Route index element={<Contributors />} />
            <Route path=":contributorId" element={<ContributorDetail />} />
            <Route path=":contributorId/stats" element={<ContributorStats />} />
          </Route>

          {/* 404 Not Found Route */}
          <Route path="*" element={
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold">404 Not Found</h2>
              <p className="text-gray-600 mt-2">The page you requested does not exist.</p>
            </div>
          } />
        </Route>
      </Routes>
    </ReactFlowProvider>
  );
}

function App() {
  return <AppRoutes />;
}

export default App;