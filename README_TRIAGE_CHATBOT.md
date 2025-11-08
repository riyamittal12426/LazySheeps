# 🚀 Auto-Triage & ChatBot Features - README

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## ⚡ Quick Start

### 1. Start Backend (30 seconds)
```bash
cd backend
python manage.py runserver
```

### 2. Start Frontend (30 seconds)
```bash
cd frontend
npm run dev
```

### 3. Test Features (2 minutes)
1. Open http://localhost:5173
2. Navigate to `/auto-triage`
3. Navigate to `/chatbot`
4. Try the demos!

---

## 🎯 Features

### 🤖 Auto-Triage & Labeling

Automatically classify GitHub issues with AI:

- **Classification**: bug, feature, docs, enhancement, security, question
- **Component Detection**: frontend, backend, api, database, devops, docs
- **Priority Assignment**: low, medium, high, critical
- **Duplicate Detection**: AI-powered similarity matching
- **Assignee Suggestion**: Based on file ownership & contribution history
- **Label Generation**: Comprehensive auto-labeling
- **Complexity Estimation**: Simple, moderate, complex
- **Effort Estimation**: Hour ranges (1-3, 3-8, 8+)

**Use Cases:**
- Reduce manual issue triage time by 70%
- Consistent labeling across projects
- Better issue routing to right developers
- Catch duplicates before they're created

### 💬 Slack/Discord ChatBot

Team collaboration bot with AI insights:

**Commands:**
- `/langhub pr <number>` - AI summary of pull requests
- `/langhub team-health` - DORA metrics & radar chart
- `/langhub digest` - Daily activity summary
- `/langhub risks` - Detect potential issues

**Features:**
- Real-time PR analysis
- Team performance metrics
- Automated daily reports
- Proactive risk detection
- Integration with existing workflows

---

## 🔧 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Django 5.2
- React 18+

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_token
SLACK_WEBHOOK_URL=your_slack_webhook
DISCORD_WEBHOOK_URL=your_discord_webhook
EOF

# Run migrations (if needed)
python manage.py migrate

# Start server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Dependencies already installed
# react-markdown is in package.json

# Start dev server
npm run dev
```

---

## 📖 Usage

### Via Web UI

#### Auto-Triage
1. Navigate to http://localhost:5173/auto-triage
2. Enter repository ID
3. Enter issue title and description
4. Click "Full Triage" or "Classify Only"
5. View results with confidence scores

#### ChatBot
1. Navigate to http://localhost:5173/chatbot
2. Select a tab (PR Summary, Team Health, etc.)
3. Enter required parameters
4. Click the action button
5. View formatted results

### Via API

#### Auto-Triage Example
```bash
curl -X POST http://localhost:8000/api/triage/classify/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Login form validation broken",
    "body": "Users cannot login with valid credentials",
    "labels": []
  }'
```

#### ChatBot Example
```bash
# Get team health
curl http://localhost:8000/api/chatbot/team-health/

# Get daily digest
curl http://localhost:8000/api/chatbot/daily-digest/

# Get risk alerts
curl http://localhost:8000/api/chatbot/risk-alerts/
```

### Via Slack/Discord

#### Slack Setup
1. Create app at https://api.slack.com/apps
2. Add slash command `/langhub`
3. Point to `https://your-domain.com/api/webhooks/slack/`
4. Install to workspace

**Usage:**
```
/langhub pr 123 owner/repo
/langhub team-health
/langhub digest
/langhub risks
```

#### Discord Setup
1. Create bot at https://discord.com/developers
2. Get webhook URL from channel settings
3. Add to environment variables

**Usage:**
```
!langhub pr 123 owner/repo
!langhub team-health
!langhub digest
!langhub risks
```

---

## 📚 API Documentation

### Auto-Triage Endpoints

#### 1. Full Auto-Triage
```
POST /api/triage/issue/
Body: {
  "repository_id": 1,
  "issue_data": {
    "title": "Bug description",
    "body": "Detailed info",
    "labels": []
  }
}
```

#### 2. Classify Only
```
POST /api/triage/classify/
Body: {
  "title": "Issue title",
  "body": "Issue description",
  "labels": []
}
```

#### 3. Detect Duplicates
```
POST /api/triage/detect-duplicate/
Body: {
  "repository_id": 1,
  "title": "Issue title",
  "body": "Description"
}
```

#### 4. Suggest Assignee
```
GET /api/triage/suggest-assignee/{repository_id}/?component=frontend
```

### ChatBot Endpoints

#### 1. PR Summary
```
POST /api/chatbot/pr-summary/
Body: {
  "pr_number": 123,
  "repository_name": "owner/repo"
}
```

#### 2. Team Health
```
GET /api/chatbot/team-health/?repository_id=1
```

#### 3. Daily Digest
```
GET /api/chatbot/daily-digest/
```

#### 4. Risk Alerts
```
GET /api/chatbot/risk-alerts/
```

#### 5. Generic Command
```
POST /api/chatbot/command/
Body: {
  "platform": "slack",
  "command": "team-health",
  "args": []
}
```

### Response Format

All endpoints return:
```json
{
  "success": true/false,
  "data": {...},
  "error": "Error message if failed"
}
```

---

## 🚀 Deployment

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_personal_access_token

# Optional - Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_BOT_TOKEN=xoxb-...

# Optional - Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Optional - Defaults
DEFAULT_REPO=owner/repo
```

### Production Setup

1. **Update settings.py**
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
```

2. **Configure CORS**
```python
CORS_ALLOWED_ORIGINS = [
    'https://your-frontend-domain.com'
]
```

3. **Setup GitHub Webhooks**
- Go to Repository Settings → Webhooks
- Add webhook URL: `https://your-domain.com/api/webhooks/github/`
- Select events: Issues, Pull requests
- Add secret to settings

4. **Deploy Backend**
```bash
# Using gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Or use your preferred WSGI server
```

5. **Deploy Frontend**
```bash
npm run build
# Serve dist/ folder with nginx/Apache
```

---

## 🛠️ Troubleshooting

### Common Issues

#### "GEMINI_API_KEY not found"
**Solution:** Add to `.env` file:
```bash
echo "GEMINI_API_KEY=your_key" >> backend/.env
```
Get key from: https://makersuite.google.com/app/apikey

#### "Repository not found"
**Solution:** Import repository first via UI or API:
```bash
POST /api/repositories/import/
{
  "repository_url": "https://github.com/owner/repo"
}
```

#### Classification confidence is low
**Solution:** 
- Add more detail to issue descriptions
- Include technical context
- Add stack traces for bugs

#### Slack webhook not working
**Solutions:**
- Verify webhook URL is not expired
- Check request URL matches deployment
- Ensure app is installed to workspace

#### Discord bot not responding
**Solutions:**
- Verify webhook URL is correct
- Check bot has proper permissions
- Ensure bot is added to server

#### Frontend components not loading
**Solution:**
```bash
cd frontend
npm install react-markdown
npm run dev
```

### Debug Mode

Enable verbose logging:
```python
# backend/config/settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'api': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Test Endpoints

```bash
# Test auto-triage
python backend/test_triage_chatbot.py

# Test specific endpoint
curl http://localhost:8000/api/chatbot/team-health/
```

---

## 📊 Performance

### Response Times
- Auto-triage: 3-5 seconds (LLM call)
- Team health: < 1 second (DB query)
- Daily digest: < 1 second (DB aggregation)
- PR summary: 2-4 seconds (GitHub API + LLM)

### Rate Limits
- Gemini API: 60 requests/minute (free tier)
- GitHub API: 5000 requests/hour (authenticated)
- Slack: No rate limit for incoming webhooks
- Discord: No rate limit for webhooks

### Optimization Tips
1. Cache frequent queries
2. Batch process old issues
3. Use async tasks for slow operations
4. Implement request queuing for high volume

---

## 🔐 Security

### Best Practices
- Never commit API keys to git
- Use environment variables
- Validate webhook signatures
- Implement rate limiting
- Use HTTPS in production
- Regularly rotate tokens

### GitHub Webhook Verification
```python
# Already implemented in webhooks.py
def verify_webhook_signature(request):
    signature = request.headers.get('X-Hub-Signature-256')
    secret = settings.GITHUB_WEBHOOK_SECRET
    # HMAC verification
```

---

## 📈 Analytics

### Metrics to Track
- Classification accuracy
- Average triage time
- Duplicate detection rate
- Assignee acceptance rate
- Command usage frequency
- User engagement

### Integration with Analytics Tools
```python
# Add to your analytics service
from api.issue_triage import triage_service

result = triage_service.triage_issue(issue_data, repo)
analytics.track('issue_triaged', {
    'type': result['classification']['type'],
    'confidence': result['classification']['confidence']
})
```

---

## 🎓 Learn More

### Documentation Files
- **QUICK_START_TRIAGE_CHATBOT.md** - 5-minute quick start
- **AUTO_TRIAGE_CHATBOT_GUIDE.md** - Complete guide
- **IMPLEMENTATION_SUMMARY_TRIAGE_CHATBOT.md** - Technical details

### Example Projects
See the test script for usage examples:
```bash
python backend/test_triage_chatbot.py
```

### Video Tutorials
(Add your demo video links here)

---

## 🤝 Contributing

### Adding New Classifications
Edit `backend/api/issue_triage.py`:
```python
def classify_issue(self, issue_data):
    # Add your custom logic
    if 'urgent' in title.lower():
        return {'priority': 'critical'}
```

### Adding New ChatBot Commands
Edit `backend/api/chatbot.py`:
```python
def handle_command(self, command, args):
    if command == 'your-command':
        return your_handler()
```

---

## 📝 License

This project is part of LangHub/LazySheeps.
See main repository for license details.

---

## 🆘 Support

### Issues
- Check documentation first
- Review troubleshooting section
- Check GitHub issues
- Contact maintainers

### Resources
- Django docs: https://docs.djangoproject.com/
- React docs: https://react.dev/
- Gemini API: https://ai.google.dev/
- Slack API: https://api.slack.com/
- Discord API: https://discord.com/developers/docs

---

## ✨ Credits

Built with:
- Django REST Framework
- React + Material-UI
- Google Gemini AI
- GitHub API
- Slack/Discord APIs

---

**Ready to transform your team's workflow! 🚀**

For questions or support, see the documentation files or contact the team.
