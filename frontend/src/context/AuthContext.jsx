import React, { createContext, useContext } from 'react';
// import { useUser, useAuth as useClerkAuth } from '@clerk/clerk-react';

const AuthContext = createContext(null);

// AUTHENTICATION DISABLED - Mock user for development
export const useAuth = () => {
  // Mock user data
  const mockUser = {
    id: 'dev-user-1',
    username: 'Developer',
    email: 'dev@langhub.local',
    firstName: 'Dev',
    lastName: 'User',
    avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Developer',
    fullName: 'Dev User',
  };
  
  return {
    user: mockUser,
    loading: false,
    isAuthenticated: true,
    signOut: () => console.log('Sign out disabled in dev mode'),
    isSignedIn: true,
  };
};

// This provider is now just a pass-through since auth is disabled
export const AuthProvider = ({ children }) => {
  return <>{children}</>;
};
