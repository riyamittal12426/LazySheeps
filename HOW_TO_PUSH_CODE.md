# 🚀 How to Push Your Code to LazySheeps App

## Step 1: Login to Get Your Authentication Token

1. Open your browser and go to: **http://localhost:5174**

2. Login to your account (or register if you haven't)

3. Open browser DevTools:
   - Press **F12** (or right-click → Inspect)
   - Go to **Application** tab
   - Click **Local Storage** → **http://localhost:5174**
   - Copy the value of **`access_token`**
   - Save it for later (you'll need it for API calls)

## Step 2: Create a Repository

### Option A: Using Web UI (Easiest)

1. Navigate to **"My Repositories"** in the sidebar (look for the server icon 🖥️)

2. Click the **"New Repository"** button

3. Fill in the form:
   - **Repository Name**: e.g., `my-project` (lowercase, hyphens allowed)
   - **Description**: Optional description of your project

4. Click **"Create Repository"**

5. **Copy the Clone URL** shown (looks like: `http://localhost:8000/git/username/my-project.git`)

### Option B: Using API

```powershell
# Replace YOUR_TOKEN with the token from Step 1
$token = "YOUR_TOKEN_HERE"

$body = @{
    name = "my-project"
    description = "My awesome project"
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/git/create/" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

## Step 3: Push Your Code

### For a NEW Project (Starting from scratch)

```powershell
# 1. Create a new directory
mkdir my-project
cd my-project

# 2. Initialize Git
git init

# 3. Create some files
echo "# My Project" > README.md
echo "print('Hello from LazySheeps!')" > main.py

# 4. Configure Git (if not done globally)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 5. Stage and commit
git add .
git commit -m "Initial commit"

# 6. Add your LazySheeps remote (use the clone URL from Step 2)
git remote add origin http://localhost:8000/git/YOUR_USERNAME/my-project.git

# 7. Push to LazySheeps!
git push -u origin main
```

### For an EXISTING Project

```powershell
# 1. Navigate to your existing project
cd C:\path\to\your\existing\project

# 2. Check current remotes
git remote -v

# 3. Add LazySheeps as a new remote
git remote add lazysheeps http://localhost:8000/git/YOUR_USERNAME/my-project.git

# 4. Push to LazySheeps
git push lazysheeps main

# Optional: Push all branches
git push lazysheeps --all
```

### For THIS LazySheeps Project (Push to your own app)

```powershell
# 1. You're already in the project!
cd C:\Users\ayush\OneDrive\Desktop\LazySheeps

# 2. Create a repository in the web UI called "lazysheeps"

# 3. Add it as a remote
git remote add myapp http://localhost:8000/git/YOUR_USERNAME/lazysheeps.git

# 4. Push everything!
git push myapp main
```

## Step 4: View Your Code in the Web UI

1. Go to **"My Repositories"** in the sidebar

2. Click on your repository name

3. **Explore**:
   - 📁 Browse files and folders
   - 💻 View code with syntax highlighting
   - 📝 Check commit history
   - 🌿 Switch between branches
   - 👥 See commit authors and timestamps

## Step 5: Make Changes and Push Again

```powershell
# 1. Make changes to your files
echo "New feature!" >> README.md

# 2. Stage and commit
git add .
git commit -m "Add new feature"

# 3. Push
git push origin main
# or if you used a different remote name:
git push lazysheeps main

# 4. Refresh the web UI to see your changes!
```

## 🎯 Quick Commands Reference

```powershell
# Clone a repository
git clone http://localhost:8000/git/username/repo.git

# Check remotes
git remote -v

# Add remote
git remote add origin http://localhost:8000/git/username/repo.git

# Push to default branch
git push origin main

# Push new branch
git checkout -b feature/new-feature
git push origin feature/new-feature

# Pull latest changes
git pull origin main

# View commit history
git log --oneline
```

## 🔧 Troubleshooting

### "fatal: repository not found"
- ✅ Check the repository exists in "My Repositories"
- ✅ Verify the username in the URL is correct
- ✅ Make sure you created the repository first (Step 2)

### "Permission denied"
- ✅ Login again to refresh your JWT token
- ✅ Check you're logged in to the web UI
- ✅ Verify the repository belongs to you

### "Failed to push some refs"
- ✅ Pull latest changes first: `git pull origin main`
- ✅ Or force push (careful!): `git push -f origin main`
- ✅ Check backend server is running on port 8000

### Backend not running?
```powershell
cd backend
python manage.py runserver
```

### Frontend not running?
```powershell
cd frontend
npm run dev
```

## 💡 Pro Tips

### 1. Multiple Remotes (GitHub + LazySheeps)
```powershell
# Add both remotes
git remote add github https://github.com/username/repo.git
git remote add lazysheeps http://localhost:8000/git/username/repo.git

# Push to both
git push github main
git push lazysheeps main

# Or create an alias to push to both at once
git remote add all https://github.com/username/repo.git
git remote set-url --add --push all https://github.com/username/repo.git
git remote set-url --add --push all http://localhost:8000/git/username/repo.git
git push all main  # Pushes to both!
```

### 2. Set Default Remote
```powershell
# Set LazySheeps as default for push
git config branch.main.remote origin
git config branch.main.merge refs/heads/main

# Now just use:
git push
```

### 3. Create Branches
```powershell
# Create and switch to new branch
git checkout -b feature/awesome-feature

# Make changes and push
git add .
git commit -m "Add awesome feature"
git push origin feature/awesome-feature

# View in web UI - use branch selector!
```

### 4. Quick Commit Alias
```powershell
# Add to your PowerShell profile
function gitpush {
    param([string]$message = "Quick update")
    git add .
    git commit -m $message
    git push
}

# Usage:
gitpush "Fix bug"
```

## 📊 What Happens Behind the Scenes

1. **You run** `git push origin main`

2. **Git sends** HTTP request to `http://localhost:8000/git/username/repo/git-receive-pack`

3. **Django backend**:
   - Validates your JWT token
   - Checks you own the repository
   - Calls `git receive-pack` via subprocess
   - Stores your code in `backend/git_repositories/username/repo.git/`

4. **You can browse** the code in the web UI:
   - Backend runs `git ls-tree` to get file list
   - Runs `git show` to get file contents
   - Runs `git log` to get commit history
   - Frontend displays everything beautifully!

## 🎉 Summary

**3 Simple Steps:**
1. ✅ Create repository in web UI (My Repositories → New Repository)
2. ✅ Add remote: `git remote add origin <clone-url>`
3. ✅ Push: `git push -u origin main`

**That's it!** Your code is now hosted on your own LazySheeps app! 🚀

---

**Need help?** Check these files:
- **GIT_SERVER_GUIDE.md** - Complete user guide
- **GIT_SERVER_README.md** - Quick reference
- **GIT_SERVER_COMPLETE.md** - Technical details

Happy coding! 🎊
