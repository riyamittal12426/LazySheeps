# Sprint Planner AI - Implementation Guide

## 🎯 Overview

The **Sprint Planner AI** is an intelligent sprint planning system that automatically analyzes your team's velocity, issue priorities, and member capacity to suggest optimal sprint backlogs and issue assignments.

### Key Features

✅ **AI-Powered Sprint Suggestions** - Automatically generates sprint plans based on data  
✅ **Velocity Analysis** - Tracks and predicts team velocity trends  
✅ **Smart Issue Assignment** - Assigns issues to team members based on capacity and workload  
✅ **Capacity Planning** - Calculates and tracks team member availability  
✅ **Completion Forecasting** - Predicts when work will be completed  
✅ **Natural Language Summaries** - AI-generated sprint overviews using Gemini

---

## 🚀 Quick Start

### 1. Generate Sprint Plan Suggestion

**Endpoint:** `POST /api/sprints/suggest/`

```bash
curl -X POST http://localhost:8000/api/sprints/suggest/ \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": 1,
    "sprint_duration_days": 14,
    "team_member_ids": [1, 2, 3]
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Sprint plan generated successfully",
  "sprint_plan": {
    "sprint_info": {
      "suggested_name": "Sprint 2024-11-09",
      "start_date": "2024-11-09",
      "end_date": "2024-11-23",
      "duration_days": 14
    },
    "team_capacity": {
      "total_story_points": 45.5,
      "total_hours": 168.0,
      "team_size": 3,
      "members": [...]
    },
    "selected_issues": {
      "total_issues": 12,
      "total_story_points": 42.0,
      "capacity_utilization": 92.3,
      "issues": [...]
    },
    "assignments": [...],
    "forecast": {
      "forecast_date": "2024-12-15",
      "sprints_needed": 2.5
    },
    "recommendations": [
      {
        "type": "success",
        "message": "Sprint capacity utilization is optimal at 92.3%"
      }
    ],
    "ai_summary": "This 14-day sprint focuses on..."
  }
}
```

---

## 📋 API Endpoints

### Sprint Planning

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sprints/suggest/` | POST | 🔥 Generate AI sprint plan |
| `/api/sprints/` | POST | Create new sprint |
| `/api/sprints/list/` | GET | List all sprints |
| `/api/sprints/{id}/` | GET | Get sprint details |
| `/api/sprints/{id}/update/` | PUT/PATCH | Update sprint |
| `/api/sprints/{id}/delete/` | DELETE | Delete sprint |
| `/api/sprints/{id}/complete/` | POST | Mark sprint complete |

### Sprint Issues

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sprints/{id}/issues/` | POST | Add issue to sprint |
| `/api/sprints/{id}/issues/{issue_id}/` | PUT/PATCH | Update sprint issue |

### Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sprints/velocity/{repo_id}/` | GET | Get velocity trends |
| `/api/sprints/capacity/` | GET | Analyze team capacity |
| `/api/sprints/forecast/{repo_id}/` | GET | Forecast completion |

---

## 🎬 Demo Workflow

### Step 1: Ask "What should we work on next sprint?"

```bash
# Generate sprint suggestion
curl -X POST http://localhost:8000/api/sprints/suggest/ \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": 1,
    "sprint_duration_days": 14
  }'
```

The AI will:
1. ✅ Analyze your team's historical velocity
2. ✅ Prioritize open issues based on multiple factors
3. ✅ Calculate team capacity
4. ✅ Select optimal issues for the sprint
5. ✅ Assign issues to team members
6. ✅ Generate completion forecast
7. ✅ Provide AI-powered recommendations

### Step 2: Create Sprint from Suggestion

```bash
curl -X POST http://localhost:8000/api/sprints/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sprint 1",
    "repository_id": 1,
    "start_date": "2024-11-09",
    "end_date": "2024-11-23",
    "planned_velocity": 42
  }'
```

### Step 3: Add Issues to Sprint

```bash
curl -X POST http://localhost:8000/api/sprints/1/issues/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "issue_type": "feature",
    "story_points": 5,
    "estimated_hours": 20,
    "priority": "high",
    "assigned_to_id": 2
  }'
```

### Step 4: Track Progress

```bash
# Get sprint details
curl http://localhost:8000/api/sprints/1/

# Update issue status
curl -X PATCH http://localhost:8000/api/sprints/1/issues/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "actual_hours": 5
  }'
```

### Step 5: Complete Sprint

```bash
curl -X POST http://localhost:8000/api/sprints/1/complete/
```

---

## 🧠 AI Features Explained

### 1. **Velocity Analysis**

The system tracks your team's actual velocity across sprints:
- Calculates average velocity from last 3 sprints
- Identifies velocity trends (improving/stable/declining)
- Uses historical data for better predictions

### 2. **Issue Prioritization**

Issues are scored based on:
- **Type** (bugs = higher priority)
- **Priority level** (critical/high/medium/low)
- **Age** (older issues score higher)
- **Labels and metadata**

### 3. **Effort Estimation**

AI predicts effort for each issue:
- Story points estimation (1-13 fibonacci scale)
- Hour estimation (story points × 4)
- Confidence level

### 4. **Smart Assignment**

Issues assigned based on:
- **Capacity** - Available hours per team member
- **Workload balance** - Even distribution
- **Utilization** - Optimal 50-70% utilization preferred
- **Historical performance**

### 5. **Completion Forecasting**

Predicts completion date using:
- Team velocity average
- Total backlog size
- Sprint duration
- Statistical analysis

---

## 📊 Data Model

### Sprint
```python
{
  "name": "Sprint 1",
  "start_date": "2024-11-09",
  "end_date": "2024-11-23",
  "status": "active",  # planned, active, completed, cancelled
  "planned_velocity": 40,
  "actual_velocity": 38,
  "completion_rate": 95.0,
  "team_capacity": 160  # hours
}
```

### SprintIssue
```python
{
  "title": "Implement feature X",
  "issue_type": "feature",  # task, bug, feature, story
  "status": "in_progress",  # todo, in_progress, completed, blocked
  "priority": "high",  # low, medium, high, critical
  "story_points": 5,
  "estimated_hours": 20,
  "actual_hours": 18,
  "assigned_to": 2,
  "ai_assigned": true,
  "ai_reasoning": "Balanced workload (45% utilized)"
}
```

### TeamMemberCapacity
```python
{
  "contributor": 1,
  "total_capacity_hours": 80,
  "allocated_hours": 60,
  "available_hours": 80,
  "remaining_hours": 20,
  "utilization_percentage": 75.0,
  "average_velocity": 15  # story points per sprint
}
```

---

## 🎨 Frontend Integration Example

```jsx
// Fetch sprint suggestion
const fetchSprintPlan = async (repositoryId) => {
  const response = await fetch('/api/sprints/suggest/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      repository_id: repositoryId,
      sprint_duration_days: 14
    })
  });
  
  const data = await response.json();
  return data.sprint_plan;
};

// Display AI recommendations
const SprintPlannerUI = ({ plan }) => {
  return (
    <div>
      <h2>{plan.sprint_info.suggested_name}</h2>
      <p>{plan.ai_summary}</p>
      
      <div className="capacity">
        <h3>Team Capacity</h3>
        <p>Total: {plan.team_capacity.total_story_points} points</p>
        <p>Utilization: {plan.selected_issues.capacity_utilization}%</p>
      </div>
      
      <div className="issues">
        <h3>Selected Issues ({plan.selected_issues.total_issues})</h3>
        {plan.selected_issues.issues.map(issue => (
          <IssueCard key={issue.issue_id} issue={issue} />
        ))}
      </div>
      
      <div className="recommendations">
        <h3>AI Recommendations</h3>
        {plan.recommendations.map((rec, i) => (
          <Alert key={i} type={rec.type}>{rec.message}</Alert>
        ))}
      </div>
    </div>
  );
};
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
```

### Settings

Sprint planning uses these default values (customizable):
- **Sprint Duration**: 14 days (2 weeks)
- **Work Hours per Day**: 8 hours
- **Work Days per Week**: 5 days
- **Default Utilization**: 75% (realistic capacity)
- **Hours per Story Point**: 4 hours
- **Max Issues per Sprint**: 15 issues

---

## 📈 Analytics Features

### Velocity Trends
```bash
GET /api/sprints/velocity/1/

Response:
{
  "average_velocity": 38.5,
  "velocity_trend": "improving",
  "sprints_analyzed": 3,
  "velocities": [40, 38, 37],
  "history": [...]
}
```

### Capacity Analysis
```bash
GET /api/sprints/capacity/?contributor_ids=1,2,3&sprint_duration_days=14

Response:
{
  "team_capacity": {
    "total_hours": 168.0,
    "team_size": 3,
    "members": [...]
  }
}
```

### Completion Forecast
```bash
GET /api/sprints/forecast/1/

Response:
{
  "forecast_date": "2024-12-15",
  "sprints_needed": 2.5,
  "total_story_points": 95.0,
  "average_velocity": 38.0
}
```

---

## 🎯 Best Practices

1. **Run Sprint Suggestions Regularly** - Generate suggestions at the start of each sprint
2. **Track Actual Hours** - Update actual hours for better future predictions
3. **Complete Sprints Properly** - Mark sprints complete to save velocity history
4. **Maintain Team Capacity** - Keep team member capacity data updated
5. **Review AI Recommendations** - Use AI suggestions as a guide, not gospel
6. **Balance Workload** - Aim for 70-80% capacity utilization
7. **Prioritize Issues** - Update issue priorities regularly

---

## 🐛 Troubleshooting

### No sprint suggestions generated?
- Ensure you have open issues in the repository
- Check that contributors exist and have activity history
- Verify repository ID is correct

### Velocity shows 0?
- Complete at least one sprint with actual_velocity data
- Use the `/complete/` endpoint to mark sprints complete

### AI summary not generating?
- Check GEMINI_API_KEY is set correctly
- Verify Gemini API quota is available
- Check server logs for API errors

---

## 🚀 Advanced Usage

### Custom Velocity Calculation
```python
from api.sprint_analytics import SprintAnalytics

velocity = SprintAnalytics.calculate_team_velocity(
    repository_id=1,
    sprints_to_analyze=5  # Last 5 sprints
)
```

### Custom Issue Prioritization
```python
prioritized = SprintAnalytics.analyze_issue_priority(repository_id=1)
# Returns issues sorted by priority score
```

### Generate Plan Programmatically
```python
from api.sprint_analytics import SprintPlannerAI

plan = SprintPlannerAI.generate_sprint_plan(
    repository_id=1,
    sprint_duration_days=10,  # 2-week sprint
    team_member_ids=[1, 2, 3, 4]
)
```

---

## 📚 Database Schema

The Sprint Planner uses these models:

1. **Sprint** - Sprint metadata and metrics
2. **SprintIssue** - Issues assigned to sprints
3. **TeamMemberCapacity** - Capacity tracking per member
4. **SprintVelocityHistory** - Historical velocity data

All models are automatically created via Django migrations.

---

## 🎉 Demo Script

Perfect for hackathon demos:

```bash
# 1. Import a repository with issues
curl -X POST http://localhost:8000/api/repositories/import/ \
  -d '{"repo_url": "https://github.com/your/repo"}'

# 2. Ask AI for sprint plan
curl -X POST http://localhost:8000/api/sprints/suggest/ \
  -d '{"repository_id": 1}'

# 3. Show the AI-generated plan with:
#    - Recommended issues
#    - Smart assignments
#    - Capacity analysis
#    - Completion forecast
#    - AI recommendations

# 4. Create the sprint
curl -X POST http://localhost:8000/api/sprints/ \
  -d '{...}'

# 5. Show velocity trends
curl http://localhost:8000/api/sprints/velocity/1/
```

---

## ⭐ Wow Factors

1. **Natural Language AI** - "What should we work on next?" gets intelligent answers
2. **Smart Assignments** - AI automatically assigns work based on capacity
3. **Predictive Analytics** - Forecasts completion dates
4. **Real-time Recommendations** - Context-aware suggestions
5. **Velocity Tracking** - Historical analysis and trend detection
6. **Capacity Planning** - Prevents overcommitment
7. **One-Click Planning** - Generate complete sprint plans instantly

---

## 📞 Support

For issues or questions:
- Check the Django logs: `python manage.py runserver`
- Verify migrations: `python manage.py showmigrations api`
- Test endpoints with curl or Postman
- Review the API documentation above

---

**Built with ❤️ for HackCBS | Powered by Django + Gemini AI**
