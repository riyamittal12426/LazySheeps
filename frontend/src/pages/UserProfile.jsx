import React from 'react';
import { UserProfile as ClerkUserProfile } from '@clerk/clerk-react';

const UserProfile = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-6">User Profile</h2>
          <ClerkUserProfile 
            appearance={{
              elements: {
                rootBox: "w-full",
                card: "bg-transparent shadow-none",
                navbar: "bg-white/5 backdrop-blur-lg rounded-lg",
                navbarButton: "text-white hover:bg-white/10",
                navbarButtonActive: "bg-purple-600 text-white",
                pageScrollBox: "bg-transparent",
                formFieldInput: "bg-white/10 border-white/20 text-white",
                formButtonPrimary: "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700",
                profileSectionTitle: "text-white",
                profileSectionContent: "text-gray-300",
                accordionTriggerButton: "text-white hover:bg-white/5",
                badge: "bg-purple-600 text-white",
              }
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
