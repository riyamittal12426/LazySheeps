# Dynamic GitHub Repository Import - User Guide

## Overview
LangHub now supports **dynamic GitHub repository import**, allowing you to analyze any public GitHub repository without hardcoded data. Just paste a repository URL and let LangHub fetch all the data automatically!

## Features

### 🔄 Real-time Data Fetching
- Import any public GitHub repository
- Automatically fetch:
  - Repository metadata (stars, forks, language)
  - All contributors with profiles
  - Up to 500 recent commits with statistics
  - All issues (excludes pull requests)
  - Collaboration patterns
  - Activity logs

### 🎯 Smart Analysis
- **AI Burnout Detection**: Automatically analyzes contributor work patterns
- **Gamification**: Awards badges, XP, and levels to contributors
- **Collaboration Network**: Identifies team relationships
- **Health Metrics**: Calculates repository health scores
- **Predictive Analytics**: Estimates project completion dates

### 🚀 Easy to Use
- Simple UI with modal dialog
- Supports multiple URL formats
- Optional GitHub token for higher rate limits
- Real-time progress updates
- Detailed import summary

---

## How to Use

### Step 1: Access the Import Feature

The **Import Repository** button is available in two locations:

1. **Dashboard** (top right corner)
2. **Repositories Page** (top right corner)

### Step 2: Enter Repository URL

Supported URL formats:
```
https://github.com/owner/repository
github.com/owner/repository
owner/repository
```

Examples:
- `https://github.com/facebook/react`
- `github.com/torvalds/linux`
- `microsoft/vscode`

### Step 3: (Optional) Add GitHub Token

For better performance and to avoid rate limits, you can provide a GitHub Personal Access Token:

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `public_repo` (for public repositories)
   - ✅ `read:user` (for user profiles)
4. Copy the generated token (starts with `ghp_`)
5. Paste it in the "GitHub Token" field

**Benefits of using a token:**
- Higher API rate limit (5,000 requests/hour vs 60)
- Faster imports
- Access to private repositories (if token has permissions)

### Step 4: Click Import

LangHub will:
1. Validate the repository URL
2. Fetch repository metadata
3. Import all contributors
4. Retrieve commits (up to 500)
5. Import issues
6. Calculate analytics and scores
7. Create collaboration relationships

This process typically takes **30-60 seconds** depending on repository size.

### Step 5: View Results

After successful import, you'll see:
- ✅ Number of contributors imported
- ✅ Number of commits processed
- ✅ Number of issues imported
- ✅ Stars and forks count

The repository will immediately appear in:
- **Dashboard** (Active Repositories section)
- **Repositories Page** (full list)
- **Contributors Page** (all imported contributors)
- **Analytics Dashboard** (with full metrics)

---

## API Endpoints

### Import Repository
```http
POST /api/repositories/import/
Content-Type: application/json

{
  "repo_url": "https://github.com/owner/repo",
  "github_token": "ghp_xxxxx"  // Optional
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Successfully imported repository-name",
  "repository": {
    "id": 1,
    "name": "repository-name",
    "url": "https://github.com/owner/repository-name",
    "stars": 1234,
    "forks": 567,
    "contributors_count": 45,
    "commits_count": 1523,
    "issues_count": 89
  }
}
```

**Response (Error):**
```json
{
  "error": "Failed to import repository: Repository not found"
}
```

### Get Import Status
```http
GET /api/repositories/import-status/
```

**Response:**
```json
{
  "repositories": [
    {
      "id": 1,
      "name": "repo-name",
      "url": "https://github.com/owner/repo",
      "stars": 1234,
      "forks": 567,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-12-01T00:00:00Z",
      "contributors_count": 45,
      "commits_count": 1523
    }
  ],
  "total": 1
}
```

---

## Management Commands

### Clear Demo Data
If you want to remove hardcoded demo data and start fresh:

```bash
cd backend
python manage.py clear_data --confirm
```

This will delete:
- All repositories
- All contributors
- All commits and issues
- All badges and collaborations
- All activity logs

**⚠️ Warning:** This action is irreversible!

### Generate Demo Data (Optional)
To populate with sample data for testing:

```bash
python manage.py generate_demo_data
```

---

## Technical Details

### Rate Limits

**Without GitHub Token:**
- 60 requests per hour per IP
- Suitable for small repositories

**With GitHub Token:**
- 5,000 requests per hour
- Recommended for production use

### Data Fetching Strategy

1. **Repository Metadata**: Single API call
2. **Contributors**: Paginated (100 per page)
3. **Commits**: Limited to 500 most recent (for performance)
4. **Issues**: All issues fetched (paginated)
5. **Delays**: 0.3-0.5 seconds between requests (rate limit protection)

### Storage

All imported data is stored in SQLite database:
- Raw JSON stored in `raw_data` field
- Parsed data in structured fields
- Relationships automatically created

### Analytics Generation

After import, LangHub automatically:
- Calculates contributor scores
- Awards badges based on achievements
- Analyzes work patterns for burnout detection
- Creates collaboration relationships
- Calculates repository health metrics

---

## Troubleshooting

### "Rate limit exceeded"
**Solution:** Wait 1 hour or use a GitHub token

### "Repository not found"
**Solution:** Check the URL format and ensure repository is public

### "Failed to fetch"
**Solution:** 
1. Check your internet connection
2. Verify GitHub API is accessible
3. Try with a smaller repository first

### "Import taking too long"
**Explanation:** Large repositories (>1000 commits) take longer. The system limits to 500 commits for performance.

### "No contributors imported"
**Possible causes:**
- Repository has no commits
- Contributors have deleted accounts
- API rate limit reached

---

## Examples

### Import React
```
URL: facebook/react
Result: ~1,600 contributors, 15,000+ commits
Time: ~2-3 minutes
```

### Import Small Project
```
URL: username/small-project
Result: 5 contributors, 100 commits
Time: ~15 seconds
```

---

## Security Notes

1. **GitHub Tokens**: Never commit tokens to version control
2. **Private Repos**: Only accessible if token has permissions
3. **Data Storage**: All data stored locally in your database
4. **API Calls**: All requests go directly to GitHub API

---

## Future Enhancements

Planned features:
- [ ] Background job processing for large repositories
- [ ] Incremental updates (re-sync existing repos)
- [ ] Support for GitLab and Bitbucket
- [ ] Webhook integration for real-time updates
- [ ] Export analysis as PDF reports
- [ ] Team comparison across multiple repos

---

## Support

For issues or questions:
1. Check this documentation
2. Review `TROUBLESHOOTING.md`
3. Check the browser console for errors
4. Review Django server logs

---

**Happy analyzing! 🚀**
