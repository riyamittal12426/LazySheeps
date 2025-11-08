# 🚀 Sprint Planner AI - Quick Start

## ⚡ Get Started in 3 Minutes

### 1. Server is Running ✅
```
http://127.0.0.1:8000
```

### 2. Test the AI Sprint Planner

**Open a new terminal** and run:

```bash
# Generate AI Sprint Plan
curl -X POST http://127.0.0.1:8000/api/sprints/suggest/ \
  -H "Content-Type: application/json" \
  -d "{\"repository_id\": 1, \"sprint_duration_days\": 14}"
```

### 3. Expected Response

```json
{
  "success": true,
  "sprint_plan": {
    "sprint_info": {
      "suggested_name": "Sprint 2024-11-09",
      "start_date": "2024-11-09",
      "end_date": "2024-11-23",
      "duration_days": 14
    },
    "team_capacity": {
      "total_story_points": 45.0,
      "team_size": 3
    },
    "selected_issues": {
      "total_issues": 10,
      "capacity_utilization": 88.9
    },
    "recommendations": [...],
    "ai_summary": "This sprint focuses on..."
  }
}
```

---

## 🎯 Demo Flow

### Step 1: Show the Problem
"How do managers decide what to work on next sprint?"
- Manual planning is time-consuming
- Hard to balance workload
- Difficult to predict completion

### Step 2: Show the Solution
**"Just ask the AI!"**

```bash
POST /api/sprints/suggest/
```

### Step 3: Highlight AI Features

1. **Velocity Analysis** ⚡
   - "AI analyzed last 3 sprints"
   - "Team velocity is improving!"

2. **Smart Prioritization** 🎯
   - "12 issues ranked by priority"
   - "Bugs prioritized higher"
   - "Older issues get attention"

3. **Intelligent Assignment** 🤖
   - "Work distributed across 3 team members"
   - "Balanced at 70% utilization"
   - "AI explains reasoning for each assignment"

4. **Predictive Forecast** 🔮
   - "Completion in 2.5 sprints"
   - "Estimated date: Dec 15, 2024"

5. **Natural Language** 💬
   - "AI-generated sprint summary"
   - "Human-readable overview"

---

## 📊 All Available Endpoints

```bash
# AI Sprint Suggestion (★ MAIN FEATURE)
POST   /api/sprints/suggest/

# Sprint Management
POST   /api/sprints/
GET    /api/sprints/list/
GET    /api/sprints/{id}/
PATCH  /api/sprints/{id}/update/
DELETE /api/sprints/{id}/delete/
POST   /api/sprints/{id}/complete/

# Sprint Issues
POST   /api/sprints/{id}/issues/
PATCH  /api/sprints/{id}/issues/{issue_id}/

# Analytics
GET    /api/sprints/velocity/{repo_id}/
GET    /api/sprints/capacity/
GET    /api/sprints/forecast/{repo_id}/
```

---

## 🎨 Frontend Integration

```javascript
// React Component Example
const SprintPlanner = () => {
  const [plan, setPlan] = useState(null);
  
  const generatePlan = async () => {
    const response = await fetch('/api/sprints/suggest/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        repository_id: 1,
        sprint_duration_days: 14
      })
    });
    
    const data = await response.json();
    setPlan(data.sprint_plan);
  };
  
  return (
    <div>
      <button onClick={generatePlan}>
        🤖 Generate Sprint Plan
      </button>
      
      {plan && (
        <div>
          <h2>{plan.sprint_info.suggested_name}</h2>
          <p>{plan.ai_summary}</p>
          
          <div className="capacity">
            <h3>Team Capacity</h3>
            <p>{plan.team_capacity.total_story_points} points</p>
            <p>{plan.selected_issues.capacity_utilization}% utilized</p>
          </div>
          
          <div className="recommendations">
            {plan.recommendations.map((rec, i) => (
              <Alert key={i} type={rec.type}>
                {rec.message}
              </Alert>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## 🐛 Troubleshooting

### Issue: Repository not found
**Solution:** Import a repository first:
```bash
POST /api/repositories/import/
{"repo_url": "https://github.com/your/repo"}
```

### Issue: No velocity data
**Solution:** Complete at least one sprint:
```bash
POST /api/sprints/{id}/complete/
```

### Issue: AI summary not generating
**Solution:** Check GEMINI_API_KEY in `.env` file

---

## 📚 Documentation

- **Full Guide:** `SPRINT_PLANNER_AI_GUIDE.md`
- **Implementation:** `SPRINT_PLANNER_IMPLEMENTATION.md`
- **Server:** http://127.0.0.1:8000
- **Admin:** http://127.0.0.1:8000/admin

---

## ✅ Checklist for Demo

- [ ] Server running on http://127.0.0.1:8000
- [ ] Test AI suggestion endpoint
- [ ] Prepare repository with issues
- [ ] Practice demo script
- [ ] Prepare talking points
- [ ] Test frontend integration (if applicable)

---

## 🎯 Key Talking Points

1. **"Watch the AI plan your sprint in seconds"**
2. **"It analyzes velocity, priorities, and capacity"**
3. **"Smart assignments balance workload automatically"**
4. **"Predicts when work will be done"**
5. **"Natural language summaries from Gemini AI"**

---

## 🏆 Wow Factor Features

⭐ One-click sprint planning  
⭐ AI-powered issue assignment  
⭐ Predictive completion dates  
⭐ Velocity trend analysis  
⭐ Natural language summaries  
⭐ Smart capacity management  

---

**You're ready to demo! 🚀**

**Time: 5-6 hours ✅**  
**Wow Factor: 8/10 ⭐⭐⭐⭐**
