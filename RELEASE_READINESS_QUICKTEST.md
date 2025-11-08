# Release Readiness Score - Quick Test Commands

## Test the Feature

### 1. Get Release Readiness Score (Lightweight)
```bash
curl http://127.0.0.1:8000/api/release-readiness/1/score/
```

### 2. Get Full Release Readiness Report
```bash
curl http://127.0.0.1:8000/api/release-readiness/1/
```

### 3. Get Just Blockers
```bash
curl http://127.0.0.1:8000/api/release-readiness/1/blockers/
```

### 4. Get Readiness Trend
```bash
curl http://127.0.0.1:8000/api/release-readiness/1/trend/?days=30
```

### 5. Get Complete Dashboard
```bash
curl http://127.0.0.1:8000/api/release-readiness/1/dashboard/
```

### 6. Get All Repositories Readiness
```bash
curl http://127.0.0.1:8000/api/release-readiness/all/
```

### 7. Compare Multiple Repositories
```bash
curl -X POST http://127.0.0.1:8000/api/release-readiness/compare/ \
  -H "Content-Type: application/json" \
  -d "{\"repository_ids\": [1, 2, 3]}"
```

## PowerShell Equivalent

### Test 1: Score Only
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/release-readiness/1/score/" -Method Get
```

### Test 2: Full Report
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/release-readiness/1/" -Method Get
```

### Test 3: Dashboard
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/release-readiness/1/dashboard/" -Method Get
```

## Expected Response Structure

### Score Only Response
```json
{
  "repository_id": 1,
  "repository_name": "your-repo",
  "score": 85.5,
  "readiness_level": "good",
  "label": "Good to Go ✅",
  "emoji": "🔵",
  "can_release": true,
  "blockers_count": 0,
  "warnings_count": 2
}
```

### Full Report Includes
- Complete score and readiness level
- All blockers and warnings
- Penalties breakdown
- Passed checks list
- Detailed metrics
- Summary statistics
- Recommendation

## Demo Questions for Hackathon

1. **"Can we ship this release?"**
   - Show the score: If >= 75, YES! If < 60, NO!
   - Point to blockers if any

2. **"What's blocking our release?"**
   - Show the blockers list
   - Explain each blocker

3. **"Is our code quality improving?"**
   - Show the trend graph
   - Point out trend direction (improving/declining)

4. **"Which repository is most ready?"**
   - Compare multiple repos
   - Show sorted list by score

5. **"What do we need to fix?"**
   - Show action items with priorities
   - Explain Critical → High → Medium

## Key Talking Points

1. **Single Score Simplicity**
   "Instead of checking 10 different tools, ONE number tells you if you're ready"

2. **Smart Blockers**
   "It doesn't just score you - it tells you EXACTLY what's blocking release"

3. **Actionable Insights**
   "Fix these 3 critical bugs, and your score jumps to 90. Data-driven decisions!"

4. **Trend Analysis**
   "Track improvement over time. Are we getting better? The data shows it!"

5. **Enterprise Ready**
   "Works with CI/CD, compares multiple repos, perfect for release managers"
