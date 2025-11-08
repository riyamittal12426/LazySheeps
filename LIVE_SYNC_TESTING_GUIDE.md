# 🧪 GitHub Live Sync Pipeline - Testing Guide

## Quick Test Commands

### **1. Start Your Servers**

```powershell
# Terminal 1: Backend
cd backend
python manage.py runserver
# Server at: http://localhost:8000

# Terminal 2: Frontend  
cd frontend
npm run dev
# Server at: http://localhost:5173

# Terminal 3: Expose for webhooks (optional for local testing)
ngrok http 8000
# Note the HTTPS URL for GitHub webhooks
```

### **2. Test API Endpoints**

```powershell
# Check sync status
curl http://localhost:8000/api/live-sync/status/

# Get live statistics
curl http://localhost:8000/api/live-sync/stats/

# View webhook logs
curl http://localhost:8000/api/live-sync/logs/

# Test repository import
curl -X POST http://localhost:8000/api/repositories/import/ \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/octocat/Hello-World",
    "import_commits": true,
    "import_issues": true
  }'
```

### **3. Test Manual Sync**

```powershell
# Get repository ID first
curl http://localhost:8000/api/repositories/

# Trigger sync for specific repository (replace 1 with actual repo ID)
curl -X POST http://localhost:8000/api/live-sync/trigger/1/ \
  -H "Content-Type: application/json" \
  -d '{"force_full_sync": false}'

# Trigger full sync for all repositories
curl -X POST http://localhost:8000/api/live-sync/trigger/ \
  -H "Content-Type: application/json" \
  -d '{"force_full_sync": true}'
```

### **4. Test Frontend Components**

Visit these URLs in your browser:

- **Live Sync Dashboard**: `http://localhost:5173/live-sync`
- **Auto-Triage Interface**: `http://localhost:5173/auto-triage` 
- **ChatBot Interface**: `http://localhost:5173/chatbot`
- **Main Dashboard**: `http://localhost:5173/dashboard`

### **5. Test Auto-Triage System**

```powershell
# Test issue classification
curl -X POST http://localhost:8000/api/triage/classify/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Login button not working on mobile",
    "body": "When I tap the login button on my iPhone, nothing happens. This is blocking users from accessing the app."
  }'

# Test duplicate detection  
curl -X POST http://localhost:8000/api/triage/detect-duplicate/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mobile login issue",
    "body": "Login fails on mobile devices",
    "repository_id": 1
  }'

# Test assignee suggestion
curl http://localhost:8000/api/triage/suggest-assignee/1/
```

### **6. Test ChatBot Commands**

```powershell
# Test PR summary
curl -X POST http://localhost:8000/api/chatbot/pr-summary/ \
  -H "Content-Type: application/json" \
  -d '{
    "pr_number": 1,
    "repository_name": "octocat/Hello-World"
  }'

# Test team health
curl http://localhost:8000/api/chatbot/team-health/

# Test daily digest
curl http://localhost:8000/api/chatbot/daily-digest/

# Test risk alerts
curl http://localhost:8000/api/chatbot/risk-alerts/
```

## 🔧 GitHub Webhook Testing

### **Setup Test Webhook (Local)**

1. **Get your ngrok URL**: `https://abc123.ngrok.io`
2. **Go to GitHub repository** → Settings → Webhooks
3. **Add webhook**:
   - URL: `https://abc123.ngrok.io/api/live-sync/webhook/`
   - Content-type: `application/json`
   - Events: Push, Pull requests, Issues, Releases
4. **Save and test**

### **Test Webhook Events**

```powershell
# Simulate GitHub push webhook
curl -X POST http://localhost:8000/api/live-sync/webhook/ \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-GitHub-Delivery: 12345" \
  -d '{
    "repository": {
      "full_name": "octocat/Hello-World"
    },
    "commits": [
      {
        "id": "abc123",
        "message": "Test commit",
        "url": "https://github.com/octocat/Hello-World/commit/abc123",
        "author": {
          "name": "Test User",
          "username": "testuser"
        },
        "timestamp": "2025-11-08T12:00:00Z"
      }
    ]
  }'
```

## ✅ Expected Results

### **1. Live Sync Dashboard** 
- Shows repository sync status
- Displays health scores and sync timestamps
- Real-time updates every 30 seconds
- Manual sync buttons work

### **2. Auto-Triage Results**
```json
{
  "classification": {
    "priority": "high",
    "labels": ["bug", "mobile", "authentication"],
    "category": "Frontend Issue",
    "confidence": 0.92
  },
  "assignee_suggestion": {
    "username": "mobile-specialist",
    "confidence": 0.85,
    "reason": "Expert in mobile authentication (12 similar issues resolved)"
  }
}
```

### **3. ChatBot Results**
```json
{
  "pr_summary": "Feature: Add mobile authentication\n\nChanges:\n- Added TouchID support\n- Implemented biometric login\n- Updated security protocols\n\nRisk: Medium (security changes)\nRecommendation: Security review required"
}
```

### **4. Team Health Metrics**
```json
{
  "dora_metrics": {
    "deployment_frequency": "2.3x per week",
    "lead_time": "2.1 days", 
    "mttr": "45 minutes",
    "change_failure_rate": "8%"
  },
  "team_health": "Good",
  "risks": ["High workload on @sarah (12 PRs)"]
}
```

## 🐛 Troubleshooting

### **Common Issues**

**1. "Repository not found" errors**
```powershell
# Check if repository is imported
curl http://localhost:8000/api/repositories/

# If not found, import it
curl -X POST http://localhost:8000/api/repositories/import/ \
  -d '{"repo_url": "https://github.com/user/repo"}'
```

**2. Webhook not receiving events**
```powershell
# Check webhook logs
curl http://localhost:8000/api/live-sync/logs/

# Verify ngrok is running
curl https://your-ngrok-url.ngrok.io/api/live-sync/status/
```

**3. AI API errors**
```bash
# Check .env file has correct API key
GEMINI_API_KEY=your_actual_api_key

# Test AI endpoint directly
curl -X POST http://localhost:8000/api/triage/classify/ \
  -d '{"title": "Test", "body": "Test issue"}'
```

**4. Frontend not loading**
```powershell
# Check if backend is running
curl http://localhost:8000/api/live-sync/status/

# Check console for CORS errors
# Add to backend settings.py: CORS_ALLOW_ALL_ORIGINS = True
```

## 🎯 Success Criteria

✅ **Backend API responding** to all endpoints  
✅ **Frontend dashboard** displaying repository data  
✅ **Auto-triage** classifying issues with AI  
✅ **ChatBot** generating PR summaries  
✅ **Live sync** updating data in real-time  
✅ **Webhooks** processing GitHub events  
✅ **DORA metrics** calculating correctly  
✅ **Team health** showing meaningful insights  

## 📊 Performance Benchmarks

- **API Response Time**: < 2 seconds
- **Webhook Processing**: < 5 seconds  
- **Full Repository Sync**: < 2 minutes
- **Dashboard Load Time**: < 3 seconds
- **AI Classification**: < 10 seconds
- **Real-time Updates**: < 30 seconds

Your GitHub Live Sync Pipeline is ready! 🚀

Test each component individually, then test the full workflow by making changes to a connected GitHub repository and watching them appear in LangHub in real-time.