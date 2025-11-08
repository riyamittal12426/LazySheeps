# GitHub Webhooks Setup Guide

## Overview
GitHub webhooks enable real-time synchronization of repository data. When events occur (commits, PRs, issues), GitHub sends immediate notifications to LangHub.

## Prerequisites
- ✅ Backend running and accessible from internet
- ✅ ngrok or similar tunneling service for local development
- ✅ GitHub repository with admin access

## Step 1: Expose Local Backend (Development)

### Using ngrok (Recommended)
```bash
# Install ngrok
# Download from https://ngrok.com/download

# Expose backend port 8000
ngrok http 8000

# You'll get a URL like: https://abc123.ngrok.io
# Note this URL - you'll need it for webhook configuration
```

### Alternative: Use a VPS/Cloud Server
Deploy backend to a server with a public IP and domain name.

## Step 2: Generate Webhook Secret

```bash
# Generate a strong random secret
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and add it to your backend `.env` file:

```env
GITHUB_WEBHOOK_SECRET=your_generated_secret_here
```

Restart your Django server:
```bash
cd backend
python manage.py runserver
```

## Step 3: Configure Webhook in GitHub

### For a Single Repository

1. **Go to Repository Settings**
   - Navigate to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings`

2. **Click "Webhooks" in left sidebar**

3. **Click "Add webhook"**

4. **Configure Webhook:**
   - **Payload URL:** `https://your-ngrok-url.ngrok.io/api/webhooks/github/`
     - Example: `https://abc123.ngrok.io/api/webhooks/github/`
   - **Content type:** `application/json`
   - **Secret:** Paste the secret from Step 2
   - **SSL verification:** Enable (recommended)
   - **Which events would you like to trigger this webhook?**
     - ✅ **Pushes** (new commits)
     - ✅ **Pull requests** (PRs opened/closed)
     - ✅ **Issues** (issues created/closed)
     - ✅ **Issue comments** (comments on issues)
     - ✅ **Pull request reviews** (code reviews)
     - ✅ **Releases** (for DORA metrics)
     - ✅ **Repositories** (repo created/deleted)
   - **Active:** ✅ Checked

5. **Click "Add webhook"**

### For an Organization (Multiple Repos)

1. **Go to Organization Settings**
   - Navigate to: `https://github.com/organizations/YOUR_ORG/settings/hooks`

2. **Follow same steps as above**
   - This will apply the webhook to ALL repositories in the organization

## Step 4: Test Webhook

### Method 1: Using GitHub UI
1. Go to your webhook settings
2. Click "Recent Deliveries"
3. Click "Redeliver" on any past event
4. Check backend logs for webhook processing

### Method 2: Make a Real Change
```bash
# Create a test commit
echo "# Webhook Test" >> README.md
git add README.md
git commit -m "Test webhook integration"
git push origin main
```

Check your backend logs:
```bash
# You should see:
INFO: Received webhook: push (ID: xxxx)
INFO: Push to owner/repo on refs/heads/main: 1 commits
INFO: Processed commit: abc1234
INFO: Webhook push processed successfully
```

### Method 3: Health Check
```bash
# Test webhook endpoint
curl https://your-ngrok-url.ngrok.io/api/webhooks/health/

# Expected response:
{
  "status": "healthy",
  "service": "github-webhook-handler",
  "version": "1.0.0"
}
```

## Step 5: Verify Data Sync

1. **Check Django Admin**
   - Go to: `http://localhost:8000/admin/`
   - Look for new `Commit` entries
   - Check `Repository` updated timestamps

2. **Check Frontend**
   - Refresh your dashboard
   - New commits should appear immediately
   - Analytics should update in real-time

## Webhook Events Handled

| Event | Trigger | Action |
|-------|---------|--------|
| **push** | New commits pushed | Creates Commit records, updates contributors |
| **pull_request** | PR opened/closed/merged | Logs PR data (future: DORA metrics) |
| **issues** | Issue opened/closed | Creates Issue records |
| **issue_comment** | Comment on issue | Logs comments |
| **pull_request_review** | Code review submitted | Logs reviews (for AI analysis) |
| **release** | New release published | Updates DORA deployment frequency |
| **repository** | Repo created/deleted | Syncs repository list |

## Troubleshooting

### Webhook Returns 401 Unauthorized
**Cause:** Invalid signature
**Fix:** 
- Verify `GITHUB_WEBHOOK_SECRET` matches GitHub webhook secret
- Restart Django server after updating .env

### Webhook Returns 404 Not Found
**Cause:** Incorrect URL
**Fix:**
- Verify URL is: `https://your-domain.com/api/webhooks/github/`
- Include trailing slash

### Webhook Returns 500 Internal Server Error
**Cause:** Backend error processing payload
**Fix:**
```bash
# Check backend logs
python manage.py runserver

# Look for error details
# Common issues:
# - Repository not in database (import it first)
# - Missing contributor data
# - Database migration needed
```

### Webhook Not Firing
**Cause:** ngrok URL changed or expired
**Fix:**
- ngrok free URLs expire after 2 hours
- Re-run ngrok and update webhook URL in GitHub
- Consider ngrok paid plan for persistent URLs

### Repository Not Found
**Cause:** Webhook received for repo not imported to LangHub
**Fix:**
```bash
# Import the repository first
curl -X POST http://localhost:8000/api/repositories/import/ \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/owner/repo"}'
```

## Security Best Practices

### 1. Always Use HTTPS
- ❌ `http://your-server.com/api/webhooks/github/`
- ✅ `https://your-server.com/api/webhooks/github/`

### 2. Keep Secret Secure
```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use environment variables in production
export GITHUB_WEBHOOK_SECRET=your_secret
```

### 3. Validate Signatures
The webhook handler automatically validates signatures using HMAC-SHA256. Don't disable this in production!

### 4. Rate Limiting
For high-traffic repos, consider rate limiting:
```python
# In settings.py
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
```

## Production Deployment

### Using Railway/Render/Heroku
```bash
# Set environment variable in platform dashboard
GITHUB_WEBHOOK_SECRET=your_secret_here

# Update webhook URL to production domain
https://your-app.railway.app/api/webhooks/github/
```

### Using AWS Lambda
```bash
# Create Lambda function
# Point API Gateway to /api/webhooks/github/
# Set GITHUB_WEBHOOK_SECRET in Lambda environment
```

### Using Docker
```dockerfile
# In docker-compose.yml
environment:
  - GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET}
```

## Monitoring

### Check Webhook Deliveries
1. Go to GitHub webhook settings
2. Click "Recent Deliveries"
3. Green checkmark = success (200 response)
4. Red X = failure (check "Response" tab for error)

### Backend Logs
```python
# In settings.py, enable logging
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'webhooks.log',
        },
    },
    'loggers': {
        'api.webhooks': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### Metrics to Track
- Webhook latency (GitHub → Backend processing time)
- Success rate (% of webhooks processed successfully)
- Event types distribution (push vs PR vs issues)
- Failed webhooks (for retry logic)

## Advanced: Webhook Queue with Celery

For high-volume repositories, process webhooks asynchronously:

```python
# In api/tasks.py
from celery import shared_task

@shared_task
def process_webhook_async(event_type, payload):
    # Process webhook in background
    handlers = {
        'push': handle_push_event,
        'pull_request': handle_pull_request_event,
        # ...
    }
    handler = handlers.get(event_type)
    if handler:
        return handler(payload)
```

```python
# In webhooks.py
from api.tasks import process_webhook_async

@csrf_exempt
def github_webhook(request):
    # Validate signature
    # ...
    
    # Queue for async processing
    process_webhook_async.delay(event, payload)
    
    # Return immediately
    return JsonResponse({'status': 'queued'}, status=202)
```

## Next Steps
1. ✅ Set up webhooks following this guide
2. ✅ Test with a small repository first
3. ✅ Monitor webhook deliveries for 24 hours
4. ✅ Scale to multiple repositories
5. ✅ Implement Celery for high-volume repos
6. ✅ Add webhook retry logic
7. ✅ Set up monitoring alerts

## Support
- GitHub Webhooks Docs: https://docs.github.com/webhooks
- LangHub Issues: Open issue on GitHub
- Webhook Debugger: https://webhook.site (for testing payloads)
