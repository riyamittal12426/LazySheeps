# Clerk Integration Guide

## Overview
Your LangHub application has been successfully migrated from custom JWT authentication to Clerk authentication.

## What Changed

### ✅ Completed Changes

1. **Package Installation**
   - Installed `@clerk/clerk-react` package
   - Added 9 Clerk-related packages

2. **Environment Configuration**
   - Created `frontend/.env` file
   - Added placeholder for `VITE_CLERK_PUBLISHABLE_KEY`

3. **Main App Setup (`main.jsx`)**
   - Wrapped entire app with `<ClerkProvider>`
   - Configured Clerk with environment variable

4. **Authentication Context (`AuthContext.jsx`)**
   - Replaced custom JWT logic with Clerk hooks
   - Now uses `useUser()` and `useAuth()` from Clerk
   - Maintained same interface for backward compatibility

5. **Routing (`App.jsx`)**
   - Removed custom login/register pages
   - Added Clerk's `<SignIn>` and `<SignUp>` components
   - Routes: `/sign-in` and `/sign-up`
   - Updated `<ProtectedRoute>` to use Clerk's `<SignedIn>/<SignedOut>`

6. **Layout Component (`Layout.jsx`)**
   - Replaced custom user menu with Clerk's `<UserButton>`
   - Shows user avatar and dropdown automatically
   - Desktop and mobile navigation updated

7. **User Profile Page (`UserProfile.jsx`)**
   - Completely replaced with Clerk's `<UserProfile>` component
   - Custom styling applied to match your theme

### 🗑️ Removed/Obsolete Files
- `pages/Login.jsx` - No longer needed (can delete)
- `pages/Register.jsx` - No longer needed (can delete)
- Custom auth backend - Still exists but no longer used by frontend

## Next Steps

### 1. Get Your Clerk Publishable Key

**Required Action:** You need to get your Clerk publishable key to complete the setup.

1. Go to [https://clerk.com](https://clerk.com)
2. Sign up or log in to your account
3. Create a new application (or select existing)
4. Go to **API Keys** in the dashboard
5. Copy your **Publishable Key** (starts with `pk_test_...` or `pk_live_...`)

### 2. Update Environment Variable

Open `frontend/.env` and replace the placeholder:

```env
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_actual_key_here
```

### 3. Configure Clerk Dashboard

In your Clerk dashboard, configure these settings:

**Application Settings:**
- Application Name: LangHub
- Application Logo: (optional - upload your logo)

**Paths:**
- Sign-in URL: `/sign-in`
- Sign-up URL: `/sign-up`
- After sign-in URL: `/dashboard`
- After sign-up URL: `/dashboard`

**Authentication Methods:**
Enable your preferred methods (recommended):
- ✅ Email + Password
- ✅ Google OAuth (optional - **See CLERK_OAUTH_SETUP.md**)
- ✅ GitHub OAuth (recommended for dev tools - **See CLERK_OAUTH_SETUP.md**)

**Note:** For detailed OAuth setup instructions, see `CLERK_OAUTH_SETUP.md`

### 4. Start the Application

Once you've added your Clerk key:

```bash
# Frontend
cd frontend
npm run dev
```

### 5. Test Authentication Flow

1. Visit `http://localhost:5173` (or your port)
2. You should be redirected to `/sign-in`
3. Click "Sign up" to create a new account
4. Complete the sign-up flow
5. You'll be redirected to `/dashboard`
6. Test the UserButton in the top-right corner

## Features You Get with Clerk

### Built-in Features
- ✅ Email/Password authentication
- ✅ Social OAuth (Google, GitHub, etc.)
- ✅ Email verification
- ✅ Password reset
- ✅ Profile management
- ✅ Multi-factor authentication (MFA)
- ✅ Session management
- ✅ User avatars
- ✅ Security & compliance

### Components Available
- `<SignIn>` - Full sign-in page
- `<SignUp>` - Full sign-up page
- `<UserButton>` - User avatar with dropdown menu
- `<UserProfile>` - Complete profile management UI

### Hooks Available
- `useUser()` - Get current user data
- `useAuth()` - Get auth state and methods
- `useClerk()` - Access Clerk instance
- `useSignIn()` - Programmatic sign-in
- `useSignUp()` - Programmatic sign-up

## Using Authentication in Your Code

### Get Current User
```jsx
import { useUser } from '@clerk/clerk-react';

function MyComponent() {
  const { user, isLoaded } = useUser();
  
  if (!isLoaded) return <div>Loading...</div>;
  
  return (
    <div>
      <p>Hello, {user.firstName}!</p>
      <img src={user.imageUrl} alt="Avatar" />
    </div>
  );
}
```

### Check Authentication Status
```jsx
import { useAuth } from '@clerk/clerk-react';

function MyComponent() {
  const { isSignedIn, isLoaded } = useAuth();
  
  if (!isLoaded) return <div>Loading...</div>;
  
  return isSignedIn ? <Dashboard /> : <LandingPage />;
}
```

### Protect Routes
```jsx
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react';

function ProtectedPage() {
  return (
    <>
      <SignedIn>
        <YourContent />
      </SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  );
}
```

## Backend Integration (Optional)

If you want to verify Clerk tokens on your Django backend:

1. **Install Clerk Python SDK**
   ```bash
   pip install clerk-backend-api
   ```

2. **Add Secret Key to Backend**
   ```python
   # backend/.env
   CLERK_SECRET_KEY=sk_test_your_secret_key
   ```

3. **Verify Tokens in Django Middleware**
   ```python
   from clerk_backend_api import Clerk
   
   clerk = Clerk(bearer_auth=os.getenv('CLERK_SECRET_KEY'))
   
   def verify_clerk_token(request):
       token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
       try:
           user = clerk.users.get_user(token)
           return user
       except Exception:
           return None
   ```

## Customization

### Theme Customization
Clerk components are already styled to match your purple/dark theme. You can further customize in `UserProfile.jsx` or other components using the `appearance` prop.

### Example - Custom Button Colors
```jsx
<SignIn 
  appearance={{
    elements: {
      formButtonPrimary: "bg-purple-600 hover:bg-purple-700",
      card: "bg-gray-900 border border-purple-500",
    }
  }}
/>
```

## Troubleshooting

### Issue: "Clerk publishable key not set"
**Solution:** Make sure you've added your key to `frontend/.env` and restarted the dev server.

### Issue: Redirecting in a loop
**Solution:** Check that your Clerk dashboard paths match your routes:
- Sign-in URL: `/sign-in`
- After sign-in: `/dashboard`

### Issue: User button not showing
**Solution:** Ensure user is signed in. The `<UserButton>` only appears when authenticated.

### Issue: Can't access user data
**Solution:** Make sure to check `isLoaded` before accessing `user`:
```jsx
const { user, isLoaded } = useUser();
if (!isLoaded) return <Loading />;
// Now safe to use user
```

## Files You Can Delete (Optional)

Once everything is working with Clerk, you can optionally clean up these files:

```bash
# Old auth pages (no longer used)
rm frontend/src/pages/Login.jsx
rm frontend/src/pages/Register.jsx

# Keep these for now (still used by other components)
# - AuthContext.jsx (adapted for Clerk)
# - Backend auth endpoints (might be useful for webhooks)
```

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk React SDK](https://clerk.com/docs/references/react/overview)
- [Clerk Dashboard](https://dashboard.clerk.com)
- [Clerk Discord Community](https://clerk.com/discord)

## Support

If you encounter any issues:
1. Check the Clerk dashboard for errors
2. Review browser console for error messages
3. Ensure environment variables are set correctly
4. Check that dev server was restarted after adding `.env`

---

**Ready to go!** Just add your Clerk publishable key and start the dev server. 🚀
