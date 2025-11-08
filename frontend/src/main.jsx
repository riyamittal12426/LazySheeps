import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ClerkProvider } from '@clerk/clerk-react';
import { DataProvider } from './context/DataContext'; // Import the provider
import App from './App';
import './index.css'; // Your Tailwind CSS entry point

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
        <DataProvider>
          <App />
        </DataProvider>
      </ClerkProvider>
    </BrowserRouter>
  </React.StrictMode>
);