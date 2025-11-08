# 🎯 Team Health Radar - Board-Level Risk Management

## Overview
**Board-level view of team health with actionable insights**
- ⏱️ Implementation Time: ~3-4 hours
- 🌟 Wow Factor: 8/10
- 💼 Use Case: Executive dashboards, team management, burnout prevention

## Features

### 📊 5 Core Health Metrics

1. **Workload Score (0-100)**
   - Tracks commits and issues over 30 days
   - Thresholds: 
     - 0-40: Healthy (Green)
     - 40-70: Moderate (Yellow)
     - 70+: Overloaded (Red)

2. **Burnout Risk (0-100)**
   - Analyzes work patterns:
     - Weekend work percentage
     - Late night commits (10pm - 6am)
     - Activity spikes (crunch time detection)
   - Weighted scoring for high-risk behaviors

3. **Review Latency (0-100)**
   - Average response time to issues/PRs
   - Tracks pending reviews
   - Thresholds:
     - 0-2 days: Excellent
     - 2-5 days: Good
     - 5-10 days: Concerning
     - 10+ days: Critical

4. **Code Churn (0-100)**
   - Measures deletions/additions ratio
   - High churn indicates:
     - Unclear requirements
     - Quality issues
     - Technical debt
   - Healthy ratio: <0.3

5. **Collaboration Score (0-100)**
   - Issue participation
   - Team interaction level
   - Inverted metric (higher is better)

### 🎨 Visualization Modes

#### Overview Mode
- **Individual Cards** for each team member
- **Health Grade** (A+ to F)
- **Priority Sorting** (Red → Yellow → Green)
- **Progress Bars** for each metric
- **Click for Details** modal

#### Heatmap Mode
- **Grid Layout** with all metrics
- **Color-Coded Cells**:
  - 🟢 Green: 0-40 (Healthy)
  - 🟡 Yellow: 40-70 (Warning)
  - 🔴 Red: 70+ (At Risk)
- **Quick Team Overview**
- **Hover for Tooltips**

### 🚨 Smart Recommendations

#### Team-Level Alerts
- Widespread burnout detection (>30% at risk)
- High average workload warnings
- Positive reinforcement for healthy teams

#### Individual Actions
- Specific recommendations per person
- Prioritized action items
- Immediate vs. preventive measures

### 📈 Overall Health Score
Weighted calculation:
- **Burnout Risk**: 35% (most important)
- **Workload**: 25%
- **Review Latency**: 20%
- **Code Churn**: 15%
- **Collaboration**: 5%

**Health Grades:**
- A+ (0-20): Exceptional
- A (20-35): Excellent
- B (35-50): Good
- C (50-65): Needs Attention
- D (65-80): At Risk
- F (80+): Critical

## API Endpoints

### GET `/api/team-health/`
Returns complete team health analysis

**Response:**
```json
{
  "success": true,
  "team_health": [
    {
      "id": 1,
      "username": "developer1",
      "avatar_url": "https://...",
      "metrics": {
        "workload": {
          "score": 45.5,
          "status": "yellow",
          "recent_commits": 35,
          "recent_issues": 8,
          "recommendation": "⚠️ Moderate workload..."
        },
        "burnout_risk": {
          "score": 62.3,
          "status": "yellow",
          "weekend_work_ratio": 15.2,
          "late_night_ratio": 8.5,
          "activity_spike": true,
          "recommendation": "⚠️ Moderate risk..."
        },
        "review_latency": {...},
        "code_churn": {...},
        "collaboration": {...}
      },
      "overall_health": {
        "score": 54.2,
        "status": "yellow",
        "health_grade": "C"
      },
      "priority": 2
    }
  ],
  "overall_stats": {
    "total_members": 10,
    "at_risk_count": 2,
    "warning_count": 4,
    "healthy_count": 4,
    "avg_workload": 48.5,
    "avg_burnout_risk": 35.2
  },
  "team_recommendations": [
    {
      "priority": "high",
      "category": "burnout",
      "message": "🚨 2 team members at high risk!...",
      "actions": [
        "Schedule mandatory time off",
        "Reduce sprint commitments"
      ]
    }
  ],
  "last_updated": "2025-01-15T10:30:00Z"
}
```

### GET `/api/team-health/<contributor_id>/`
Detailed health metrics for individual contributor

**Response:**
```json
{
  "success": true,
  "contributor": {
    "id": 1,
    "username": "developer1",
    "avatar_url": "https://...",
    "email": "dev@example.com"
  },
  "metrics": { /* same as above */ },
  "overall_health": { /* same as above */ },
  "detailed_recommendations": [
    {
      "category": "Workload",
      "status": "critical",
      "message": "🚨 Heavy workload!...",
      "actions": [
        "Defer 2-3 non-critical tasks",
        "Decline new assignments this sprint",
        "Request help from team members"
      ]
    }
  ]
}
```

## Frontend Component

### Usage
```jsx
import TeamHealthRadar from './components/TeamHealthRadar';

function App() {
  return <TeamHealthRadar />;
}
```

### Features
- **Auto-refresh** on mount
- **Two view modes**: Overview & Heatmap
- **Interactive cards** with hover effects
- **Detail modal** for deep-dive analysis
- **Real-time status** indicators
- **Pulsing animations** for critical issues
- **Responsive design** for all screen sizes

### Color System
```css
Green (#10b981):  Healthy, no action needed
Yellow (#f59e0b): Warning, monitor closely
Red (#ef4444):    At risk, immediate action required
```

## Implementation

### Backend Setup
1. ✅ Created `backend/api/team_health.py` (500+ lines)
2. ✅ Added API endpoints to `urls.py`
3. ✅ Comprehensive calculations for all metrics
4. ✅ Smart recommendation engine

### Frontend Setup
1. ✅ Created `TeamHealthRadar.jsx` component (600+ lines)
2. ✅ Created `TeamHealthRadar.css` with animations
3. ✅ Added route to `App.jsx`: `/team-health`
4. ✅ Added navigation to `Layout.jsx`

### Usage
```bash
# Backend
cd backend
python manage.py runserver

# Frontend
cd frontend
npm run dev

# Visit: http://localhost:5174/team-health
```

## Use Cases

### 1. **Weekly Team Review**
- Review heatmap with managers
- Identify at-risk team members
- Plan workload redistribution

### 2. **1-on-1 Meetings**
- Open individual detail modal
- Discuss specific metrics
- Create action plans

### 3. **Sprint Planning**
- Check team capacity before committing
- Avoid overloading at-risk members
- Balance work distribution

### 4. **Quarterly Health Reports**
- Export team health trends
- Share with leadership
- Demonstrate proactive management

### 5. **Burnout Prevention**
- Early warning system
- Automated alerts for critical cases
- Preventive interventions

## Business Value

### For Managers
- **Objective data** vs. subjective feelings
- **Early warning system** for team issues
- **Actionable recommendations** not just metrics
- **Time savings** - automated analysis

### For Team Members
- **Visibility** into workload balance
- **Advocacy** for better work-life balance
- **Recognition** for healthy practices
- **Support** when struggling

### For Organizations
- **Reduced turnover** via burnout prevention
- **Higher productivity** from balanced teams
- **Better planning** with capacity insights
- **Cultural improvement** - data-driven care

## Metrics Accuracy

### Data Sources
- **Git commits**: Timestamp, lines changed
- **Issues**: Creation, assignment, closure times
- **Activity patterns**: Day of week, hour of day
- **Code changes**: Additions, deletions

### Limitations
- Based on quantitative data only
- Doesn't capture context (complexity, meetings)
- Self-reported data may be missing
- Requires sufficient historical data (30+ days)

### Best Practices
- Combine with qualitative feedback
- Use as starting point for conversations
- Don't use for performance reviews
- Focus on support, not punishment

## Customization

### Adjusting Thresholds
Edit `backend/api/team_health.py`:
```python
# Workload thresholds
status = 'green' if score < 40 else 'yellow' if score < 70 else 'red'

# Burnout weights
risk_score += weekend_ratio * 25  # Adjust weight
```

### Adding Metrics
1. Create calculation function in `team_health.py`
2. Add to `team_health_radar` response
3. Update frontend `TeamHealthRadar.jsx`
4. Add visualization in CSS

### Custom Recommendations
Edit recommendation functions:
```python
def get_workload_recommendation(score):
    if score < 40:
        return "✅ Custom message..."
```

## Future Enhancements

### Phase 2
- [ ] Historical trend charts (90-day view)
- [ ] Email alerts for critical cases
- [ ] Slack integration for notifications
- [ ] Export to PDF reports

### Phase 3
- [ ] Machine learning for predictive burnout
- [ ] Peer comparison (anonymized)
- [ ] Team composition analysis
- [ ] Integration with HR systems

### Phase 4
- [ ] Real-time updates via WebSocket
- [ ] Custom metric builder
- [ ] Role-based access control
- [ ] Multi-team comparison

## Testing

### Sample Data
Use the existing contributors and their commits/issues. For better testing:

```bash
# Generate more activity
cd backend
python manage.py shell

from api.models import Contributor, Commit, Issue
from django.utils import timezone
from datetime import timedelta

# Create test commits with various patterns
contributor = Contributor.objects.first()

# Weekend commits (burnout indicator)
for i in range(10):
    Commit.objects.create(
        contributor=contributor,
        repository=contributor.repositories.first(),
        sha=f"weekend_{i}",
        message="Weekend work",
        created_at=timezone.now() - timedelta(days=i*7, hours=12),  # Saturdays
        additions=100,
        deletions=50
    )
```

### Frontend Testing
1. Open http://localhost:5174/team-health
2. Click "Overview" and "Heatmap" tabs
3. Click individual cards for details
4. Verify color coding matches scores
5. Test responsive design (mobile)

## Troubleshooting

### No Data Showing
- Ensure contributors have commits/issues in last 30 days
- Check API endpoint: http://localhost:8000/api/team-health/
- Verify CORS settings allow frontend

### Incorrect Scores
- Review calculation logic in `team_health.py`
- Check timestamp data quality
- Verify timezone settings in Django

### Performance Issues
- Add database indexes on `created_at` fields
- Implement caching for expensive calculations
- Consider background job for updates

## Demo Script

### 30-Second Pitch
"Team Health Radar gives you a board-level view of your team's wellbeing. See who's at risk of burnout, who's overloaded, and get actionable recommendations - all in one beautiful dashboard."

### 2-Minute Demo
1. Show overview mode - explain color coding
2. Point out at-risk member (red card)
3. Click for detailed breakdown
4. Switch to heatmap view
5. Highlight team recommendations
6. Emphasize actionable insights

### Key Talking Points
- ✅ Proactive vs. reactive management
- ✅ Objective data for difficult conversations
- ✅ Burnout prevention = retention
- ✅ Better planning with capacity visibility
- ✅ Cultural signal - we care about wellbeing

## Success Metrics

### Week 1
- [ ] All team members visible
- [ ] Accurate scores for test data
- [ ] Managers using weekly

### Month 1
- [ ] 1 burnout case prevented
- [ ] Workload redistribution success
- [ ] Positive team feedback

### Quarter 1
- [ ] Reduced turnover
- [ ] Improved team health scores
- [ ] Integration into standard process

## Conclusion

Team Health Radar transforms invisible risks into visible, actionable insights. By combining objective metrics with smart recommendations, it empowers managers to support their teams proactively - before small issues become big problems.

**Built with care for teams that care about their people.** ❤️
