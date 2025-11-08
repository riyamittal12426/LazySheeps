import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
// import { SignIn, SignUp, useAuth as useClerkAuth } from '@clerk/clerk-react';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import PricingPage from './pages/PricingPage';
import Dashboard from './pages/Dashboard';
import EnhancedDashboard from './pages/EnhancedDashboard';
import Repositories from './pages/Repositories';
import RepositoryDetail from './pages/RepositoryDetail';
import Contributors from './pages/Contributors';
import ContributorDetail from './pages/ContributorDetail';
import ContributorStats from './pages/ContributorStats';
import UserProfile from './pages/UserProfile';
import GitHubCallback from './pages/GitHubCallback';
import GitHubAppCallback from './pages/GitHubAppCallback';
import RepositorySelection from './pages/RepositorySelection';
import TeamHealthRadar from './components/TeamHealthRadar';
import AutoTriage from './components/AutoTriage';
import ChatBot from './components/ChatBot';
import Login from './pages/Login';
import Register from './pages/Register';
import { ReactFlowProvider } from '@xyflow/react';

// AUTHENTICATION DISABLED - All routes are now accessible
const ProtectedRoute = ({ children }) => {
  // Always return children without authentication check
  return children;
};

function AppRoutes() {
  return (
    <ReactFlowProvider>
      <Routes>
        {/* Landing Page */}
        <Route path="/" element={<LandingPage />} />
        
        {/* Marketing Pages */}
        <Route path="/pricing" element={<PricingPage />} />
        
        {/* Auth Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Redirect old routes to new /app prefix */}
        <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
        <Route path="/analytics" element={<Navigate to="/app/analytics" replace />} />
        <Route path="/repositories/*" element={<Navigate to="/app/repositories" replace />} />
        <Route path="/contributors/*" element={<Navigate to="/app/contributors" replace />} />
        
        {/* GitHub OAuth Routes */}
        <Route path="/auth/github/callback" element={<GitHubCallback />} />
        <Route path="/auth/github-app/callback" element={<GitHubAppCallback />} />
        
        {/* Onboarding Routes */}
        <Route path="/onboarding/repositories" element={
          <ProtectedRoute>
            <RepositorySelection />
          </ProtectedRoute>
        } />
        
        {/* App Routes with Layout */}
        <Route path="/app" element={<Layout />}>
          {/* Redirect /app to dashboard */}
          <Route index element={<Navigate to="/app/dashboard" replace />} />
          
          {/* Dashboard Routes */}
          <Route path="dashboard" element={<Dashboard />} />
          
          {/* Enhanced Dashboard with Analytics */}
          <Route path="analytics" element={<EnhancedDashboard />} />
          
          {/* User Profile */}
          <Route path="profile" element={<UserProfile />} />
          
          {/* Team Health Radar */}
          <Route path="team-health" element={<TeamHealthRadar />} />

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

          {/* Auto-Triage & ChatBot Routes */}
          <Route path="auto-triage" element={<AutoTriage />} />
          <Route path="chatbot" element={<ChatBot />} />

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