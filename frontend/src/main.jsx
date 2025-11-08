import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ClerkProvider } from '@clerk/clerk-react';
import { DataProvider } from './context/DataContext'; // Import the provider
import App from './App';
import './index.css'; // Your Tailwind CSS entry point

// Import your Clerk publishable key
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  console.error("⚠️ Missing Clerk Publishable Key! Add it to frontend/.env file");
  console.error("The app will load but authentication won't work.");
  console.error("Get your key from: https://dashboard.clerk.com");
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    {PUBLISHABLE_KEY ? (
      <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
        <BrowserRouter>
          <DataProvider>
            <App />
          </DataProvider>
        </BrowserRouter>
      </ClerkProvider>
    ) : (
      <BrowserRouter>
        <DataProvider>
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column',
            alignItems: 'center', 
            justifyContent: 'center', 
            height: '100vh',
            background: 'linear-gradient(to bottom right, #1f2937, #7c3aed, #1f2937)',
            color: 'white',
            padding: '20px',
            textAlign: 'center'
          }}>
            <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️ Clerk Not Configured</h1>
            <p style={{ marginBottom: '1rem', maxWidth: '600px' }}>
              Your Clerk publishable key is missing or invalid.
            </p>
            <div style={{ 
              background: 'rgba(0,0,0,0.3)', 
              padding: '20px', 
              borderRadius: '10px',
              marginTop: '20px',
              textAlign: 'left',
              maxWidth: '800px'
            }}>
              <p style={{ marginBottom: '10px' }}><strong>To fix this:</strong></p>
              <ol style={{ marginLeft: '20px' }}>
                <li>Go to <a href="https://dashboard.clerk.com" target="_blank" style={{ color: '#a78bfa' }}>dashboard.clerk.com</a></li>
                <li>Create or select your application</li>
                <li>Go to API Keys</li>
                <li>Copy your Publishable Key (starts with pk_test_ or pk_live_)</li>
                <li>Open <code>frontend/.env</code> file</li>
                <li>Replace the key: <code>VITE_CLERK_PUBLISHABLE_KEY=your_key_here</code></li>
                <li>Restart the dev server</li>
              </ol>
            </div>
            <button 
              onClick={() => window.location.reload()}
              style={{
                marginTop: '20px',
                padding: '10px 20px',
                background: '#7c3aed',
                border: 'none',
                borderRadius: '5px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '1rem'
              }}
            >
              Reload Page
            </button>
          </div>
        </DataProvider>
      </BrowserRouter>
    )}
  </React.StrictMode>
);