# 🎯 Git Server - Quick Reference

## ⚡ Quick Commands

### Create Repository (Web UI)
1. Navigate to **"My Repositories"** in sidebar
2. Click **"New Repository"**
3. Enter name and description
4. Copy the clone URL

### Push Code
```bash
# New project
git init
git add .
git commit -m "Initial commit"
git remote add origin http://localhost:8000/git/USERNAME/REPO.git
git push -u origin main

# Existing project
git remote add lazysheeps http://localhost:8000/git/USERNAME/REPO.git
git push lazysheeps main
```

### Clone Repository
```bash
git clone http://localhost:8000/git/USERNAME/REPO.git
```

## 🗂️ Project Structure

```
LazySheeps/
├── backend/
│   ├── api/
│   │   ├── git_server.py          # Git server implementation
│   │   └── migrations/
│   │       └── 0005_add_local_git_support.py
│   ├── git_repositories/          # Storage (auto-created)
│   │   └── username/
│   │       └── repo.git/
│   └── test_git_server.py         # Test suite
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── GitRepositoryBrowser.jsx    # Browse repos
│       │   └── CreateRepository.jsx        # Create repos
│       └── pages/
│           └── MyRepositories.jsx          # List repos
│
├── GIT_SERVER_GUIDE.md            # Full user guide
├── GIT_SERVER_COMPLETE.md         # Implementation details
└── start_git_server.ps1           # Quick start script
```

## 🔗 Key URLs

| Purpose | URL |
|---------|-----|
| My Repositories | http://localhost:5174/my-repositories |
| Browse Repo | http://localhost:5174/git/USERNAME/REPO |
| Create Repo API | http://localhost:8000/api/git/create/ |
| Clone URL | http://localhost:8000/git/USERNAME/REPO.git |

## 🧪 Testing

```powershell
# Set your JWT token
$env:LAZYSHEEPS_TOKEN = "your_token_here"

# Run tests
python backend\test_git_server.py
```

Get token from browser: `F12` → `Application` → `Local Storage` → `access_token`

## 📊 API Endpoints

### Repository Management
- `POST /api/git/create/` - Create repository
- `GET /api/git/<user>/repositories/` - List repositories

### Git Operations
- `GET /git/<user>/<repo>/info/refs` - Git info
- `POST /git/<user>/<repo>/git-receive-pack` - Push
- `POST /git/<user>/<repo>/git-upload-pack` - Pull

### Browsing
- `GET /api/git/<user>/<repo>/browse/` - File tree
- `GET /api/git/<user>/<repo>/file/?path=<path>` - File content
- `GET /api/git/<user>/<repo>/commits/` - Commit history

## 🎨 Features

✅ Full Git push/pull support
✅ Web-based file browser
✅ Syntax-highlighted code viewer
✅ Commit history with authors
✅ Branch management
✅ Local filesystem storage
✅ Team collaboration ready

## 🚀 Start Servers

```powershell
# Backend
cd backend
python manage.py runserver

# Frontend (new terminal)
cd frontend
npm run dev
```

## 📚 Documentation

- **[GIT_SERVER_GUIDE.md](./GIT_SERVER_GUIDE.md)** - Complete user guide with tutorials
- **[GIT_SERVER_COMPLETE.md](./GIT_SERVER_COMPLETE.md)** - Technical implementation details

## 💡 Pro Tips

1. **Multiple Remotes**: Keep GitHub AND LazySheeps
   ```bash
   git remote add github https://github.com/user/repo.git
   git remote add lazysheeps http://localhost:8000/git/user/repo.git
   git push github main  # Push to GitHub
   git push lazysheeps main  # Push to LazySheeps
   ```

2. **Branch Workflow**:
   ```bash
   git checkout -b feature/new-feature
   git push lazysheeps feature/new-feature
   ```

3. **Quick Commit**:
   ```bash
   git add . && git commit -m "Quick fix" && git push
   ```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Repository not found" | Check username in URL, verify repo exists |
| "Permission denied" | Re-login to get fresh JWT token |
| "Push failed" | Ensure backend running on port 8000 |
| "Clone failed" | Check network, verify clone URL |

## 🎯 What's Next?

- [ ] Test by creating your first repository
- [ ] Push code from an existing project
- [ ] Browse files in the web UI
- [ ] Share with team members
- [ ] Set up webhooks for auto-deploy
- [ ] Integrate with CI/CD pipeline

---

**Ready to go! Open http://localhost:5174/my-repositories and create your first repo! 🚀**
