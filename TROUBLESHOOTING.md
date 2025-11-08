# 🔧 Troubleshooting Guide

## ✅ Issue Fixed: AFRAME ReferenceError

### Problem:
The `react-force-graph` library was causing an error:
```
Uncaught ReferenceError: AFRAME is not defined
```

### Solution:
Replaced `react-force-graph` with a custom Canvas-based network visualization that:
- Uses native HTML5 Canvas API
- No external dependencies needed
- Simpler and more reliable
- Still interactive (click nodes to see details)

---

## 🚀 Current Status

### ✅ Working:
- Backend API (Django) - Port 8000
- Frontend (React + Vite) - Port 5174
- Database with sample data
- All API endpoints functional

### 📝 Changes Made:
1. Replaced `CollaborationNetwork.jsx` with Canvas implementation
2. Removed dependency on `react-force-graph`
3. Kept all functionality (click, hover, visualization)

---

## 🌐 How to Access

1. **Main Dashboard**: http://localhost:5174/
2. **Analytics Page**: http://localhost:5174/analytics
3. **Contributors**: http://localhost:5174/contributors
4. **Repositories**: http://localhost:5174/repositories

---

## 🎯 Quick Test

Open http://localhost:5174/analytics and check:
- ✅ Overview tab loads
- ✅ Leaderboard tab shows rankings
- ✅ Collaboration tab shows network graph (Canvas)
- ✅ Insights tab shows statistics

---

## 🐛 If Still Having Issues

### Clear Browser Cache:
1. Press `Ctrl + Shift + R` (hard refresh)
2. Or open DevTools (F12) → Network tab → Check "Disable cache"

### Check Console:
1. Open DevTools (F12)
2. Go to Console tab
3. Look for any errors

### Restart Frontend:
```bash
cd frontend
npm run dev
```

---

## 📊 API Endpoints to Test

### Test Leaderboard:
```
http://localhost:8000/api/leaderboard/
```

### Test Dashboard Stats:
```
http://localhost:8000/api/dashboard/stats/
```

### Test Collaboration Network:
```
http://localhost:8000/api/collaboration/network/
```

All should return JSON data.

---

## ✨ New CollaborationNetwork Features

The Canvas-based implementation includes:
- **Circular Layout**: Contributors arranged in a circle
- **Color Coding**: 
  - Purple = High score (>5000)
  - Blue = Medium score (2000-5000)
  - Green = Regular (<2000)
  - Red = Selected
- **Interactive**: Click nodes to see details
- **Visual Edges**: Line thickness = collaboration strength
- **Legend**: Shows color meanings
- **Responsive**: Scales with container

---

## 🎨 What You'll See

### Analytics Dashboard:
- 4 stat cards at top
- 4 tabs: Overview, Leaderboard, Collaboration, Insights
- Real-time data from API

### Leaderboard:
- Top 10 contributors
- Medals for top 3 (🥇🥈🥉)
- XP and levels
- Activity streaks
- Stats (commits, issues, reviews)

### Collaboration Network:
- Canvas-based graph
- Contributors as colored circles
- Lines showing collaborations
- Click to select and see details

### Insights:
- Activity trends
- Quick stats with emojis
- Weekly patterns

---

## 💡 Tips for Demo

1. **Start with Analytics page** to wow judges
2. **Show the leaderboard** to demonstrate gamification
3. **Interact with network graph** by clicking nodes
4. **Navigate to a contributor's stats** to show burnout detection
5. **Emphasize the AI features** (burnout prediction)

---

## 🎯 All Features Working

✅ Gamification (Leaderboard, Badges, XP)
✅ AI Burnout Detection
✅ Collaboration Network (Canvas-based)
✅ Repository Health Scoring
✅ Predictive Analytics
✅ Activity Trends
✅ Dashboard Statistics

---

## 📞 Quick Commands

### Restart Both Servers:

**Backend:**
```bash
cd backend
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Check if APIs Work:
Open in browser:
- http://localhost:8000/api/leaderboard/
- http://localhost:8000/api/dashboard/stats/

Should see JSON responses.

---

## ✅ Success Checklist

- [ ] Frontend loads at http://localhost:5174/
- [ ] No console errors (F12 → Console)
- [ ] Can navigate between tabs
- [ ] Leaderboard shows contributors
- [ ] Network graph displays (canvas with circles)
- [ ] Can click on network nodes
- [ ] Stats load on Overview tab

---

## 🚀 Ready for Demo!

Everything should now work smoothly. The Canvas implementation is:
- More stable
- Easier to debug
- No dependency issues
- Still impressive visually

**You're ready to win! 🏆**
