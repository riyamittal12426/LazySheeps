# 🎨 Clerk OAuth Appearance Customization

## Quick Enable in Clerk Dashboard

### Method 1: Use Clerk Dev Keys (Instant - Recommended for Testing)

1. Go to https://dashboard.clerk.com
2. Select your LangHub application
3. Navigate to: **User & Authentication** → **Social Connections**
4. Find **Google**:
   - Click on it
   - Toggle **"Enabled"** to ON
   - Select **"Use development keys from Clerk"**
   - Click Save
5. Find **GitHub**:
   - Click on it
   - Toggle **"Enabled"** to ON
   - Select **"Use development keys from Clerk"**
   - Click Save

**Result**: OAuth buttons appear immediately! No additional configuration needed.

---

## What Users Will See

### Sign-In Page
When users visit `/sign-in`, they'll see:

```
┌────────────────────────────────────┐
│                                    │
│       Sign in to LangHub           │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ 🔵 Continue with Google      │ │ ← Google button
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ 🐙 Continue with GitHub      │ │ ← GitHub button
│  └──────────────────────────────┘ │
│                                    │
│  ────────── or ──────────         │
│                                    │
│  Email address                     │
│  ┌──────────────────────────────┐ │
│  │ user@example.com             │ │
│  └──────────────────────────────┘ │
│                                    │
│  Password                          │
│  ┌──────────────────────────────┐ │
│  │ ••••••••                     │ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │       Continue               │ │
│  └──────────────────────────────┘ │
│                                    │
│  Don't have an account? Sign up    │
│                                    │
└────────────────────────────────────┘
```

---

## OAuth Flow

### Google Sign-In Flow
```
1. User clicks "Continue with Google"
   ↓
2. Redirected to Google OAuth consent screen
   ↓
3. User selects Google account
   ↓
4. Google asks for permission to share:
   - Email address
   - Basic profile info (name, picture)
   ↓
5. User clicks "Allow"
   ↓
6. Redirected back to your app
   ↓
7. Clerk creates user account automatically
   ↓
8. User lands on /dashboard
   ✅ Done!
```

### GitHub Sign-In Flow
```
1. User clicks "Continue with GitHub"
   ↓
2. Redirected to GitHub authorization page
   ↓
3. GitHub shows app permissions:
   - Read user email
   - Read user profile
   ↓
4. User clicks "Authorize LangHub"
   ↓
5. Redirected back to your app
   ↓
6. Clerk creates user account automatically
   ↓
7. User lands on /dashboard
   ✅ Done!
```

---

## Customizing Button Appearance

If you want to customize how the OAuth buttons look, you can modify them in your components:

### Option 1: Customize in Sign-In Page

```jsx
// In App.jsx, update the SignIn component
<SignIn 
  routing="path" 
  path="/sign-in"
  appearance={{
    elements: {
      // The container for all social buttons
      socialButtonsBlockButton: `
        flex items-center justify-center gap-3
        w-full px-6 py-3 rounded-lg
        bg-white hover:bg-gray-50
        text-gray-900 font-semibold
        border-2 border-gray-200
        transition-all duration-200
        shadow-sm hover:shadow-md
      `,
      
      // The provider icon (Google/GitHub logo)
      socialButtonsProviderIcon: "w-5 h-5",
      
      // The text inside the button
      socialButtonsBlockButtonText: "font-semibold text-base",
      
      // The "or" divider between OAuth and email
      dividerLine: "bg-purple-500/30",
      dividerText: "text-purple-300 text-sm font-medium",
      
      // Overall card styling
      card: "bg-gray-900 shadow-2xl border border-purple-500/20",
      
      // Form inputs
      formFieldInput: "bg-white/10 border-white/20 text-white",
      
      // Primary button (Continue)
      formButtonPrimary: `
        bg-gradient-to-r from-purple-600 to-blue-600
        hover:from-purple-700 hover:to-blue-700
        text-white font-bold
        shadow-lg hover:shadow-xl
      `,
    }
  }}
/>
```

### Option 2: Dark Theme OAuth Buttons

```jsx
<SignIn 
  appearance={{
    elements: {
      // Dark styled OAuth buttons
      socialButtonsBlockButton: `
        bg-white/10 hover:bg-white/20
        text-white border border-white/20
        backdrop-blur-lg
      `,
      
      // Make logos pop on dark background
      socialButtonsProviderIcon: "w-6 h-6 brightness-110",
      
      // Styling for dark theme
      card: "bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900",
      dividerLine: "bg-white/20",
      dividerText: "text-white/60",
    }
  }}
/>
```

### Option 3: Minimal Style

```jsx
<SignIn 
  appearance={{
    elements: {
      // Minimal, clean OAuth buttons
      socialButtonsBlockButton: `
        bg-transparent hover:bg-white/5
        text-white border border-white/30
        rounded-full px-8 py-3
      `,
      
      socialButtonsBlockButtonText: "text-sm uppercase tracking-wider",
      
      // Hide the divider for cleaner look
      dividerRow: "hidden",
    }
  }}
/>
```

---

## Individual Provider Styling

If you want different styles for Google vs GitHub buttons:

```jsx
<SignIn 
  appearance={{
    elements: {
      // Target specific providers
      'socialButtonsBlockButton[data-provider="google"]': `
        bg-white hover:bg-blue-50
        text-gray-900 border-2 border-blue-300
      `,
      
      'socialButtonsBlockButton[data-provider="github"]': `
        bg-gray-900 hover:bg-gray-800
        text-white border-2 border-gray-700
      `,
    }
  }}
/>
```

---

## Testing Checklist

After enabling OAuth, test these scenarios:

### Google OAuth
- [ ] Button appears on sign-in page
- [ ] Button shows Google logo
- [ ] Clicking redirects to Google
- [ ] Can select Google account
- [ ] Can authorize permissions
- [ ] Redirects back to app
- [ ] Creates account automatically
- [ ] Avatar shows from Google profile
- [ ] Email is pre-filled from Google

### GitHub OAuth
- [ ] Button appears on sign-in page
- [ ] Button shows GitHub (Octocat) logo
- [ ] Clicking redirects to GitHub
- [ ] Can authorize application
- [ ] Redirects back to app
- [ ] Creates account automatically
- [ ] Avatar shows from GitHub profile
- [ ] Username imported from GitHub

### Account Linking
- [ ] Sign up with Google first
- [ ] Sign out
- [ ] Try to sign in with GitHub (same email)
- [ ] Clerk prompts to link accounts
- [ ] Can see both connections in profile

---

## What Data You Get

### From Google OAuth:
```javascript
{
  id: "user_abc123",
  firstName: "John",
  lastName: "Doe",
  email: "john@gmail.com",
  imageUrl: "https://lh3.googleusercontent.com/...",
  externalAccounts: [{
    provider: "google",
    emailAddress: "john@gmail.com",
    verified: true,
    approvedScopes: ["email", "profile"]
  }]
}
```

### From GitHub OAuth:
```javascript
{
  id: "user_xyz789",
  username: "johndoe",
  firstName: "John",
  lastName: "Doe",
  email: "john@example.com",
  imageUrl: "https://avatars.githubusercontent.com/u/...",
  externalAccounts: [{
    provider: "github",
    username: "johndoe",
    emailAddress: "john@example.com",
    verified: true,
    approvedScopes: ["user:email", "read:user"]
  }]
}
```

---

## Using OAuth Data in Your App

### Display GitHub Username
```jsx
import { useUser } from '@clerk/clerk-react';

function UserProfile() {
  const { user } = useUser();
  
  const githubAccount = user?.externalAccounts.find(
    account => account.provider === 'github'
  );
  
  return (
    <div>
      {githubAccount && (
        <a href={`https://github.com/${githubAccount.username}`}>
          @{githubAccount.username}
        </a>
      )}
    </div>
  );
}
```

### Show Connected Accounts
```jsx
function ConnectedAccounts() {
  const { user } = useUser();
  
  return (
    <div>
      <h3>Connected Accounts</h3>
      {user?.externalAccounts.map(account => (
        <div key={account.id}>
          <span>{account.provider}</span>
          <span>{account.emailAddress}</span>
          {account.verified && <span>✓ Verified</span>}
        </div>
      ))}
    </div>
  );
}
```

### Import GitHub Repos (Bonus Feature!)
```jsx
function GitHubRepoImporter() {
  const { user } = useUser();
  
  const githubAccount = user?.externalAccounts.find(
    account => account.provider === 'github'
  );
  
  async function importRepos() {
    if (!githubAccount) return;
    
    // Use GitHub username to fetch repos
    const username = githubAccount.username;
    const response = await fetch(`https://api.github.com/users/${username}/repos`);
    const repos = await response.json();
    
    // Now you can import these repos into your LangHub backend!
    console.log('User repos:', repos);
  }
  
  return (
    <button onClick={importRepos}>
      Import My GitHub Repos
    </button>
  );
}
```

---

## Production Considerations

### Rate Limits
- **Clerk Dev Keys**: Limited to development use
- **Production**: Use your own OAuth apps for unlimited users

### Branding
- **Clerk Dev Keys**: Shows "via Clerk" in consent screen
- **Your OAuth Apps**: Shows your app name and logo

### Domains
- **Dev**: Works on localhost automatically
- **Production**: Must whitelist your production domain

---

## Summary

### ✅ Quick Enable (2 minutes):
1. Clerk Dashboard
2. Social Connections
3. Toggle Google → ON (use dev keys)
4. Toggle GitHub → ON (use dev keys)
5. Test!

### ✨ Result:
- Beautiful OAuth buttons appear
- Users can sign in with Google/GitHub
- Zero configuration needed
- Works immediately

### 🎨 Customize (Optional):
- Use `appearance` prop to style buttons
- Match your app's theme
- Add custom animations

### 🚀 Ready to Use:
Your app now has enterprise-grade OAuth authentication! 🎉

---

**Pro Tip**: Test with your own Google and GitHub accounts first to ensure everything works smoothly!
