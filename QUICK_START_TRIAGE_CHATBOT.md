# 🚀 Quick Start: Auto-Triage & ChatBot

## ⚡ 5-Minute Setup

### 1. Backend Setup (2 minutes)

```bash
cd backend

# Install dependencies (if not already done)
pip install -r requirements.txt

# Add to .env file
echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env
echo "GITHUB_TOKEN=your_github_token_here" >> .env

# Run server
python manage.py runserver
```

### 2. Frontend Setup (1 minute)

```bash
cd frontend

# Install react-markdown (only needed once)
npm install react-markdown

# Run dev server
npm run dev
```

### 3. Test Features (2 minutes)

**Option A: Using Test Script**
```bash
cd backend
python test_triage_chatbot.py
```

**Option B: Using UI**
1. Open http://localhost:5173
2. Navigate to Auto-Triage page
3. Navigate to ChatBot page
4. Test the features!

---

## 🎯 Quick Demo

### Auto-Triage Example

**Input:**
```
Title: "Login form crashes on invalid password"
Body: "Getting HTTP 500 error when entering wrong password..."
```

**Output:**
```json
{
  "type": "bug",
  "component": "backend",
  "priority": "critical",
  "assignee": "backend_dev_123",
  "labels": ["bug", "component:backend", "priority:critical"],
  "is_duplicate": false
}
```

### ChatBot Example

**Command:** `/langhub team-health`

**Output:**
```
📊 DORA Metrics
• Deployment Frequency: 2.3/day ✅
• Lead Time: 18.5 hours ✅
• MTTR: 4.2 hours ✅
• Change Failure Rate: 8.5% ⚠️
```

---

## 🔌 API Endpoints (Quick Reference)

### Auto-Triage
- `POST /api/triage/issue/` - Full triage
- `POST /api/triage/classify/` - Classification only
- `POST /api/triage/detect-duplicate/` - Duplicate detection
- `GET /api/triage/suggest-assignee/{id}/` - Assignee suggestion

### ChatBot
- `POST /api/chatbot/pr-summary/` - PR summary
- `GET /api/chatbot/team-health/` - Team metrics
- `GET /api/chatbot/daily-digest/` - Daily activity
- `GET /api/chatbot/risk-alerts/` - Risk detection

### Webhooks
- `POST /api/webhooks/slack/` - Slack integration
- `POST /api/webhooks/discord/` - Discord integration

---

## 📱 Slack Setup (5 minutes)

1. **Create App**: https://api.slack.com/apps → "Create New App"
2. **Add Slash Command**: 
   - Command: `/langhub`
   - Request URL: `https://your-domain.com/api/webhooks/slack/`
3. **Get Webhook URL**: Incoming Webhooks → Activate → Copy URL
4. **Add to .env**:
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
   ```

**Test It:**
```
/langhub team-health
/langhub digest
```

---

## 🎮 Discord Setup (5 minutes)

1. **Create Bot**: https://discord.com/developers → New Application
2. **Get Webhook**: Channel Settings → Integrations → Webhooks
3. **Add to .env**:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

**Test It:**
```
!langhub team-health
!langhub digest
```

---

## 🎨 Frontend Components

### Add to Your App

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AutoTriage from './components/AutoTriage';
import ChatBot from './components/ChatBot';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/triage" element={<AutoTriage />} />
        <Route path="/chatbot" element={<ChatBot />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🔥 Common Issues & Fixes

### "GEMINI_API_KEY not found"
**Fix:** Add to backend/.env:
```
GEMINI_API_KEY=your_key_here
```
Get key from: https://makersuite.google.com/app/apikey

### "Repository not found"
**Fix:** Import a repository first:
```bash
# In your app
POST /api/repositories/import/
{
  "repository_url": "https://github.com/owner/repo"
}
```

### "No commits found"
**Fix:** Ensure repository has been synced:
```bash
POST /api/repositories/{id}/sync/
```

### Slack webhook not working
**Fix:** Check webhook URL is correct and not expired. Regenerate if needed.

---

## 📊 File Structure

```
backend/
  api/
    issue_triage.py          # Auto-triage logic
    chatbot.py               # ChatBot service
    triage_chatbot_views.py  # API endpoints
    webhooks.py              # GitHub webhook integration

frontend/
  src/
    components/
      AutoTriage.jsx         # Auto-triage UI
      ChatBot.jsx            # ChatBot UI

AUTO_TRIAGE_CHATBOT_GUIDE.md # Full documentation
QUICK_START_TRIAGE_CHATBOT.md # This file
test_triage_chatbot.py       # Test script
```

---

## ✅ Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] GEMINI_API_KEY in .env
- [ ] GITHUB_TOKEN in .env (for PR summaries)
- [ ] Tested auto-triage via UI
- [ ] Tested chatbot via UI
- [ ] (Optional) Slack webhook configured
- [ ] (Optional) Discord webhook configured

---

## 🎯 Next Steps

1. **Test locally** using the UI components
2. **Set up webhooks** for GitHub auto-triage
3. **Configure Slack/Discord** for team collaboration
4. **Customize** classification rules for your needs
5. **Schedule** daily digests with cron jobs
6. **Monitor** triage accuracy and improve prompts

---

## 💡 Pro Tips

1. **Start with classification only** - Test without DB dependencies
2. **Use UI for testing** - Easier than curl/Postman
3. **Check console logs** - Backend logs show detailed triage results
4. **Customize prompts** - Edit `issue_triage.py` for better accuracy
5. **Integrate gradually** - Start with manual, then automate

---

## 📚 Resources

- **Full Guide**: AUTO_TRIAGE_CHATBOT_GUIDE.md
- **Test Script**: backend/test_triage_chatbot.py
- **API Docs**: See guide for complete API reference

---

## 🆘 Support

Having issues? Check:
1. Django server is running
2. Environment variables are set
3. Dependencies are installed
4. Database has repositories (for full triage)

Still stuck? Check the logs:
```bash
# Backend logs
tail -f backend/logs/django.log

# Or run with verbose output
python manage.py runserver --verbosity 2
```

---

**Time to first demo**: 5 minutes ⚡
**Wow factor**: High 🚀
**Setup difficulty**: Easy 👍

Happy coding! 🎉
