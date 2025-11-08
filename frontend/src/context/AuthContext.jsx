import React, { createContext, useContext } from 'react';
import { useUser, useAuth as useClerkAuth } from '@clerk/clerk-react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const clerkAuth = useClerkAuth();
  const { user, isLoaded } = useUser();
  
  return {
    user: user ? {
      id: user.id,
      username: user.username || user.firstName || 'User',
      email: user.primaryEmailAddress?.emailAddress,
      firstName: user.firstName,
      lastName: user.lastName,
      avatar_url: user.imageUrl,
      fullName: user.fullName,
    } : null,
    loading: !isLoaded,
    isAuthenticated: !!user && isLoaded,
    signOut: clerkAuth.signOut,
    ...clerkAuth,
  };
};

// This provider is now just a pass-through since Clerk handles everything
export const AuthProvider = ({ children }) => {
  return <>{children}</>;
};
