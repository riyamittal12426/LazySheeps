# 🔄 GitHub to LangHub Live Sync Pipeline

## Complete Step-by-Step Setup Guide

### 🎯 **What This Pipeline Does**

This system creates a **real-time connection** between your GitHub repositories and LangHub, automatically:
- ✅ **Syncs new commits** as they're pushed
- ✅ **Updates DORA metrics** when PRs are merged  
- ✅ **Tracks issues and labels** in real-time
- ✅ **Monitors team health** continuously
- ✅ **Triggers AI analysis** for new issues
- ✅ **Broadcasts updates** to your dashboard

---

## 📋 **Prerequisites**

Before setting up the pipeline, ensure you have:

1. **LangHub Backend Running**
```powershell
cd backend
python manage.py runserver
# Should be accessible at http://localhost:8000
```

2. **Public URL for Webhooks** (Choose one method):
   - **Option A**: Use ngrok for testing
   - **Option B**: Deploy to cloud (Heroku, AWS, etc.)
   - **Option C**: Use local tunnel service

3. **GitHub Repository Admin Access**
   - You need admin rights to add webhooks to repositories

---

## 🚀 **Step 1: Expose Your Local Server**

### **Method A: Using ngrok (Recommended for Testing)**

```powershell
# Install ngrok if you haven't already
# Download from: https://ngrok.com/download

# Expose your Django server
ngrok http 8000

# You'll get a URL like: https://abc123.ngrok.io
# Note this URL - you'll need it for webhooks
```

### **Method B: Using localtunnel**

```powershell
# Install localtunnel globally
npm install -g localtunnel

# Expose your Django server
lt --port 8000 --subdomain langhub-sync

# You'll get: https://langhub-sync.loca.lt
```

---

## 🔧 **Step 2: Configure Environment Variables**

Add these to your `backend/.env` file:

```bash
# Your existing variables...
GEMINI_API_KEY=your_gemini_key
SLACK_WEBHOOK_URL=your_slack_webhook
DISCORD_WEBHOOK_URL=your_discord_webhook

# New webhook configuration
GITHUB_WEBHOOK_SECRET=your_secure_webhook_secret
PUBLIC_WEBHOOK_URL=https://your-ngrok-url.ngrok.io

# Optional: Enable debug logging
WEBHOOK_DEBUG=True
```

**Generate a secure webhook secret:**
```powershell
# Use this Python command to generate a secure secret
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🌐 **Step 3: Set Up GitHub Webhooks**

For each repository you want to sync:

### **3.1: Navigate to Repository Settings**
1. Go to your GitHub repository
2. Click **Settings** tab
3. Click **Webhooks** in the left sidebar
4. Click **Add webhook**

### **3.2: Configure Webhook**

**Payload URL:** `https://your-ngrok-url.ngrok.io/api/live-sync/webhook/`

**Content type:** `application/json`

**Secret:** `your_secure_webhook_secret` (from .env file)

**Events:** Select these events:
- ✅ **Push events**
- ✅ **Pull request events**  
- ✅ **Issue events**
- ✅ **Release events**
- ✅ **Issue comment events**

**Active:** ✅ Checked

### **3.3: Test Webhook**
Click **Add webhook** and GitHub will send a test ping.

---

## 🛠️ **Step 4: Import Existing Repositories**

### **4.1: Using the API**

```powershell
# Import a repository
curl -X POST http://localhost:8000/api/repositories/import/ \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/username/repository",
    "import_commits": true,
    "import_issues": true,
    "import_contributors": true
  }'
```

### **4.2: Using the Frontend**
1. Start frontend: `cd frontend && npm run dev`
2. Navigate to: `http://localhost:5173/repositories`
3. Click **Import Repository**
4. Enter GitHub URL and click **Import**

---

## 🔄 **Step 5: Configure Auto-Sync Settings**

### **5.1: Set Sync Preferences for Each Repository**

```bash
# Configure auto-sync for repository ID 1
curl -X POST http://localhost:8000/api/live-sync/configure/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "auto_sync_enabled": true,
    "sync_interval": 3600,
    "full_sync_interval": 86400,
    "webhook_events": ["push", "pull_request", "issues", "release"]
  }'
```

### **5.2: Enable Real-time Notifications**

```bash
# Configure Slack notifications
curl -X POST http://localhost:8000/api/chatbot/configure/ \
  -H "Content-Type: application/json" \
  -d '{
    "enable_push_notifications": true,
    "enable_pr_notifications": true,
    "enable_issue_notifications": true,
    "slack_channel": "#dev-updates"
  }'
```

---

## 📊 **Step 6: Monitor Live Sync Status**

### **6.1: Check Sync Status**

```bash
# Get overall sync status
curl http://localhost:8000/api/live-sync/status/

# Get live statistics
curl http://localhost:8000/api/live-sync/stats/

# View webhook logs
curl http://localhost:8000/api/live-sync/logs/
```

### **6.2: Frontend Monitoring**
Navigate to: `http://localhost:5173/live-sync-dashboard`

---

## 🧪 **Step 7: Test the Pipeline**

### **7.1: Test Push Events**
1. Make a commit to your connected repository
2. Push to GitHub
3. Check LangHub dashboard - should update within seconds

### **7.2: Test Issue Events**
1. Create a new issue on GitHub
2. Watch it appear in LangHub with AI classification

### **7.3: Test PR Events**  
1. Create and merge a pull request
2. Observe DORA metrics update automatically

### **7.4: Manual Sync Trigger**

```bash
# Force full sync for repository ID 1
curl -X POST http://localhost:8000/api/live-sync/trigger/1/ \
  -H "Content-Type: application/json" \
  -d '{"force_full_sync": true}'

# Sync all repositories
curl -X POST http://localhost:8000/api/live-sync/trigger/ \
  -H "Content-Type: application/json" \
  -d '{"force_full_sync": false}'
```

---

## 🔍 **Troubleshooting**

### **Common Issues & Solutions**

**1. Webhook Not Receiving Events**
```bash
# Check if your server is accessible
curl https://your-ngrok-url.ngrok.io/api/live-sync/status/

# Check webhook logs
curl http://localhost:8000/api/live-sync/logs/

# Verify GitHub webhook settings
# - Check the payload URL
# - Verify the secret matches .env file
# - Ensure events are selected
```

**2. Repository Not Found Errors**
```bash
# List all imported repositories
curl http://localhost:8000/api/repositories/

# Import missing repository
curl -X POST http://localhost:8000/api/repositories/import/ \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo"}'
```

**3. Sync Performance Issues**
```bash
# Check sync history for a repository
curl http://localhost:8000/api/live-sync/history/1/

# Configure lighter sync (fewer events)
curl -X POST http://localhost:8000/api/live-sync/configure/1/ \
  -d '{"webhook_events": ["push", "release"]}'
```

---

## 📈 **Advanced Configuration**

### **Production Deployment**

**1. Use Real Domain**
```bash
# Instead of ngrok, use your production domain
PUBLIC_WEBHOOK_URL=https://langhub.yourdomain.com
```

**2. Enable Rate Limiting**
```bash
# Add to .env
WEBHOOK_RATE_LIMIT=100  # requests per minute
WEBHOOK_RATE_LIMIT_BURST=10
```

**3. Database Optimization**
```bash
# Enable connection pooling
DATABASE_POOL_SIZE=20
DATABASE_POOL_MAX_OVERFLOW=30
```

**4. Caching Configuration**
```bash
# Use Redis for better performance
CACHE_BACKEND=redis
REDIS_URL=redis://localhost:6379/1
```

---

## 🎯 **Expected Results**

Once setup is complete, you'll have:

✅ **Real-time Dashboard Updates** - See commits, PRs, issues as they happen  
✅ **Automated DORA Metrics** - Deployment frequency, lead time calculated live  
✅ **Smart Issue Triage** - New issues automatically classified and assigned  
✅ **Team Health Monitoring** - Continuous visibility into team performance  
✅ **Slack/Discord Notifications** - Team gets notified of important changes  
✅ **Historical Data Sync** - All past data imported and continuously updated  

---

## 🚀 **Quick Start Commands**

```powershell
# 1. Start the backend
cd backend && python manage.py runserver

# 2. Start ngrok (new terminal)
ngrok http 8000

# 3. Add webhook to GitHub repository
# URL: https://your-url.ngrok.io/api/live-sync/webhook/
# Events: push, pull_request, issues, release

# 4. Import repository
curl -X POST http://localhost:8000/api/repositories/import/ \
  -d '{"repo_url": "https://github.com/user/repo"}'

# 5. Test the pipeline
# Make a commit to GitHub and watch LangHub update!
```

---

## 📞 **Support**

If you encounter issues:
1. Check the **webhook logs**: `/api/live-sync/logs/`
2. Verify **repository import**: `/api/repositories/`  
3. Test **manual sync**: `/api/live-sync/trigger/{repo_id}/`
4. Review **Django logs** in your terminal
5. Check **GitHub webhook delivery** in repository settings

Your GitHub to LangHub pipeline should now be live and automatically syncing! 🎉