# Self-Hosted Git Server - User Guide

## 🚀 Quick Start

Your LazySheeps application now has a complete self-hosted Git server! You can push and pull code just like GitHub, GitLab, or Bitbucket.

## 📋 Prerequisites

1. **Backend server running** on `http://localhost:8000`
2. **Frontend running** on `http://localhost:5174`
3. **Git installed** on your machine
4. **User account** created in LazySheeps

## 🎯 Step-by-Step Tutorial

### 1. Create a New Repository

**Option A: Via Web UI**
1. Navigate to "My Repositories" in the sidebar
2. Click "New Repository" button
3. Enter repository name (e.g., `my-project`)
4. Add description (optional)
5. Click "Create Repository"
6. Copy the clone URL shown

**Option B: Via API**
```bash
curl -X POST http://localhost:8000/api/git/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "my-project",
    "description": "My awesome project"
  }'
```

Response:
```json
{
  "status": "success",
  "message": "Repository created successfully",
  "repository": {
    "id": 1,
    "name": "my-project",
    "description": "My awesome project",
    "clone_url": "http://localhost:8000/git/username/my-project.git",
    "ssh_url": "git@localhost:username/my-project.git",
    "default_branch": "main"
  }
}
```

### 2. Push Your First Code

**For a New Project:**
```bash
# Create a new directory
mkdir my-project
cd my-project

# Initialize Git repository
git init

# Create a README file
echo "# My Project" > README.md

# Add and commit files
git add .
git commit -m "Initial commit"

# Add remote (use the clone_url from creation step)
git remote add origin http://localhost:8000/git/username/my-project.git

# Push to the server
git push -u origin main
```

**For an Existing Project:**
```bash
# Navigate to your project
cd /path/to/existing/project

# Add the new remote
git remote add lazysheeps http://localhost:8000/git/username/my-project.git

# Push your code
git push lazysheeps main
```

### 3. Browse Your Repository

**Via Web UI:**
1. Go to "My Repositories" in the sidebar
2. Click on your repository name
3. Browse files, view code, check commits!

**Via API:**
```bash
# List your repositories
curl http://localhost:8000/api/git/username/repositories/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Browse repository files
curl http://localhost:8000/api/git/username/my-project/browse/?path=/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# View a specific file
curl http://localhost:8000/api/git/username/my-project/file/?path=README.md \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get commit history
curl http://localhost:8000/api/git/username/my-project/commits/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Clone an Existing Repository

```bash
# Clone via HTTPS
git clone http://localhost:8000/git/username/my-project.git

# Navigate into the cloned repository
cd my-project

# Make changes
echo "New content" >> README.md
git add README.md
git commit -m "Update README"

# Push changes back
git push origin main
```

## 🔧 Advanced Usage

### Multiple Remotes

You can have multiple remotes (GitHub + LazySheeps):

```bash
# Add LazySheeps as a remote
git remote add lazysheeps http://localhost:8000/git/username/my-project.git

# Add GitHub as a remote
git remote add github https://github.com/username/my-project.git

# Push to both
git push lazysheeps main
git push github main
```

### Branching

```bash
# Create and switch to a new branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push the branch
git push lazysheeps feature/new-feature

# View all branches via API
curl http://localhost:8000/api/git/username/my-project/commits/?branch=feature/new-feature \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Working with Teams

Share the clone URL with team members:
```
http://localhost:8000/git/username/my-project.git
```

Team members can clone and collaborate:
```bash
git clone http://localhost:8000/git/username/my-project.git
cd my-project
# Make changes...
git push origin main
```

## 📁 Repository Storage

All repositories are stored locally in:
```
backend/git_repositories/
├── username1/
│   ├── project1.git/
│   └── project2.git/
└── username2/
    └── project3.git/
```

These are **bare repositories** (server-side `.git` folders).

## 🎨 Web Interface Features

### Repository Browser
- **File Tree**: Browse all files and directories
- **Breadcrumb Navigation**: Easy navigation through folders
- **Code Viewer**: Syntax-highlighted code display
- **Branch Selector**: Switch between branches
- **Commit History**: View recent commits with authors and timestamps
- **File Information**: File sizes and types

### Create Repository Page
- Simple form to create new repositories
- Instant clone URL generation
- Quick setup commands
- Copy-to-clipboard functionality

## 🔐 Authentication

Currently using JWT token authentication:

1. **Login** to get your access token
2. Token is stored in `localStorage`
3. Include token in API requests: `Authorization: Bearer YOUR_TOKEN`
4. For Git operations (push/pull), the backend automatically validates your session

## 📊 API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/git/create/` | POST | Create new repository |
| `/api/git/<username>/repositories/` | GET | List user's repositories |
| `/api/git/<username>/<repo>/browse/` | GET | Browse repository files |
| `/api/git/<username>/<repo>/file/` | GET | Get file content |
| `/api/git/<username>/<repo>/commits/` | GET | Get commit history |
| `/git/<username>/<repo>/info/refs` | GET | Git protocol info |
| `/git/<username>/<repo>/git-upload-pack` | POST | Git pull/fetch |
| `/git/<username>/<repo>/git-receive-pack` | POST | Git push |

## 🧪 Testing Checklist

- [ ] Create repository via web UI
- [ ] Create repository via API
- [ ] Initialize local Git project
- [ ] Add remote and push code
- [ ] Verify files appear in `git_repositories/`
- [ ] Browse repository via web UI
- [ ] View file contents in browser
- [ ] Check commit history
- [ ] Clone repository to new location
- [ ] Make changes and push
- [ ] Switch branches
- [ ] View branch in web UI

## ⚠️ Troubleshooting

### "Repository not found"
- Verify repository exists: Check `backend/git_repositories/username/repo.git`
- Check username spelling in URL
- Ensure you're authenticated (token in localStorage)

### "Permission denied"
- Login to get valid JWT token
- Check token expiry (re-login if needed)
- Verify you own the repository

### "Failed to push"
- Check backend server is running on port 8000
- Verify remote URL is correct: `git remote -v`
- Ensure main branch exists: `git branch`
- Try pushing with force (if safe): `git push -f origin main`

### Git asks for password
- HTTPS URLs may prompt for credentials
- Use your LazySheeps username and password
- Or configure credential helper: `git config credential.helper store`

## 🎉 What You Can Do Now

✅ **Host your own code** - No need for GitHub/GitLab for private projects
✅ **Full version control** - All Git features work (branches, commits, history)
✅ **Team collaboration** - Share repositories with your team
✅ **Code browsing** - Beautiful web interface to view code
✅ **Local storage** - All data stays on your server
✅ **Git workflow** - Standard `git push`, `git pull`, `git clone`
✅ **Multiple remotes** - Use alongside GitHub/GitLab
✅ **Commit tracking** - View full commit history with authors and timestamps

## 🚀 Next Steps

1. **Try it out**: Create your first repository and push some code
2. **Explore the UI**: Browse files, view commits, switch branches
3. **Share with team**: Give team members the clone URL
4. **Integrate webhooks**: Auto-deploy on push (coming soon)
5. **Add SSH support**: For secure, password-free authentication (future feature)

## 💡 Pro Tips

- Use meaningful commit messages
- Create branches for features: `git checkout -b feature/my-feature`
- Push regularly to keep the server in sync
- Browse code in the web UI to review changes
- Share the clone URL with collaborators
- Keep the backend running for Git operations

Enjoy your self-hosted Git server! 🎊
