# GitHub OAuth Setup Guide

## Overview
This guide will help you set up GitHub OAuth authentication for OrgLens, enabling users to sign in with GitHub and select repositories to import (similar to Vercel's onboarding flow).

## 1. Create a GitHub OAuth App

1. Go to GitHub Settings: https://github.com/settings/developers
2. Click "OAuth Apps" → "New OAuth App"
3. Fill in the following details:
   - **Application name**: `OrgLens` (or your preferred name)
   - **Homepage URL**: `http://localhost:5173` (for development)
   - **Authorization callback URL**: `http://localhost:3000/auth/github/callback`
   - **Application description**: `Understanding your codebase and connecting with experts`

4. Click "Register application"
5. You'll see your **Client ID** - copy this
6. Click "Generate a new client secret" and copy the **Client Secret**

## 2. Configure Backend Environment Variables

Update your `backend/.env` file with the GitHub OAuth credentials:

```env
# GitHub OAuth Settings
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
GITHUB_REDIRECT_URI=http://localhost:3000/auth/github/callback
```

Replace `your_github_client_id_here` and `your_github_client_secret_here` with the values from step 1.

## 3. Run Database Migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

## 4. Start the Backend Server

```bash
cd backend
python manage.py runserver
```

The backend should start on `http://localhost:8000`

## 5. Start the Frontend Server

```bash
cd frontend
npm install  # if not already done
npm run dev
```

The frontend should start on `http://localhost:5173`

## 6. Test the Flow

1. **Navigate to Sign In**: Go to `http://localhost:5173/sign-in`
2. **Click "Continue with GitHub"**: This will redirect you to GitHub
3. **Authorize the App**: GitHub will ask you to authorize OrgLens
4. **Select Repositories**: After authorization, you'll be redirected to the repository selection page
5. **Import Repositories**: Select the repositories you want to import and click "Import"
6. **Dashboard**: You'll be redirected to the dashboard with your imported repositories

## API Endpoints

### Backend Endpoints

#### 1. Get GitHub OAuth URL
```
GET /api/auth/github/url/
```
Returns the GitHub OAuth authorization URL.

#### 2. GitHub OAuth Callback
```
POST /api/auth/github/callback/
Body: { "code": "authorization_code" }
```
Exchanges the authorization code for access tokens and user info.

#### 3. Fetch User's GitHub Repositories
```
GET /api/github/repositories/
Headers: 
  - Authorization: Bearer {jwt_token}
  - X-GitHub-Token: {github_access_token}
```
Returns list of user's GitHub repositories.

#### 4. Import Selected Repositories
```
POST /api/github/import/
Headers:
  - Authorization: Bearer {jwt_token}
  - X-GitHub-Token: {github_access_token}
Body: {
  "repositories": ["owner/repo1", "owner/repo2"]
}
```
Imports the selected repositories into OrgLens.

## Frontend Routes

### New Routes Added

1. **GitHub OAuth Callback**: `/auth/github/callback`
   - Handles the OAuth callback from GitHub
   - Exchanges code for tokens
   - Redirects to repository selection or dashboard

2. **Repository Selection**: `/onboarding/repositories`
   - Vercel-like interface to select repositories
   - Shows all user's accessible repos
   - Allows filtering and searching
   - Batch import functionality

## Features

### Repository Selection Page Features

- ✅ **Search**: Filter repositories by name
- ✅ **Filter**: Show all/public/private repositories
- ✅ **Select All/Deselect All**: Bulk selection
- ✅ **Repository Cards**: Show repo details (stars, forks, language, etc.)
- ✅ **Batch Import**: Import multiple repositories at once
- ✅ **Skip Option**: Skip import and go directly to dashboard

### Authentication Features

- ✅ **Dual Auth**: Supports both Clerk and GitHub OAuth
- ✅ **JWT Tokens**: Secure authentication with JWT
- ✅ **GitHub Token Storage**: Stores GitHub access token for API calls
- ✅ **User Profile**: Creates user profile with GitHub info

## Troubleshooting

### Issue: "GitHub token required" error
**Solution**: Make sure the `X-GitHub-Token` header is being sent with repository requests. The token is stored in localStorage after OAuth callback.

### Issue: Callback URL mismatch
**Solution**: Ensure the callback URL in GitHub OAuth settings matches exactly: `http://localhost:3000/auth/github/callback`

### Issue: CORS errors
**Solution**: Check that `django-cors-headers` is configured correctly in `settings.py` and the frontend origin is allowed.

### Issue: Repositories not loading
**Solution**: 
1. Check that the GitHub token is valid
2. Verify the user has granted `repo` scope permissions
3. Check browser console for API errors

## Production Deployment

When deploying to production:

1. **Update GitHub OAuth App**:
   - Homepage URL: `https://yourdomain.com`
   - Callback URL: `https://yourdomain.com/auth/github/callback`

2. **Update Environment Variables**:
   ```env
   GITHUB_REDIRECT_URI=https://yourdomain.com/auth/github/callback
   ```

3. **Update CORS Settings**: Add your production domain to `CORS_ALLOWED_ORIGINS` in `settings.py`

4. **HTTPS Required**: GitHub OAuth requires HTTPS in production

## Next Steps

After setting up GitHub OAuth:

1. ✅ Test the complete flow from sign-in to repository import
2. ✅ Customize the repository selection UI to match your brand
3. ✅ Add repository sync functionality (webhooks)
4. ✅ Implement repository access controls
5. ✅ Add repository activity tracking

## Support

For issues or questions:
- Check the Django logs: `backend/` terminal
- Check the React logs: Browser console
- Review API responses in Network tab

Happy coding! 🚀
