# Katalyst 🚀# Katalyst - Hackathon Winner 🏆



**AI-Powered Developer Analytics Platform**

https://github.com/user-attachments/assets/7496afda-b3e3-4e1d-b03f-ddc43982b7a1

> Understand your codebase. Connect with contributors. Amplify your development velocity.

*Katalyst: Understanding your codebase and connecting with experts, powered by  .*

[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)Built for the  con Hackathon ([05/04/2025]).

[![React](https://img.shields.io/badge/React-19.0-blue.svg)](https://reactjs.org/)

[![Python](https://img.shields.io/badge/Python-3.x-yellow.svg)](https://www.python.org/)## The Problem



---Finding the right expert or understanding code history in large organizations is time-consuming and inefficient. Key knowledge often stays siloed or buried in commit logs.



## 📖 Table of Contents## Our Solution: Katalyst



- [Overview](#overview)Katalyst connects to your GitHub organization, analyzes repositories, commits, and contributors, and uses ** ** to generate insightful summaries. It helps you:

- [The Problem](#the-problem)

- [Our Solution](#our-solution)*   Instantly find contributors with specific expertise.

- [Key Features](#key-features)*   Understand individual contributions through AI-generated profiles.

- [Tech Stack](#tech-stack)*   Query your codebase's history and activity using natural language.

- [Architecture](#architecture)*   Interact with contributor "digital twins" (AI based on their work) for context before direct contact.

- [Getting Started](#getting-started)

- [Features Deep Dive](#features-deep-dive)## Core Features

- [API Documentation](#api-documentation)

- [Database Schema](#database-schema)*   🚀 **Dynamic Repository Import** - Import any GitHub repository with a single click

- [Screenshots](#screenshots)*   🤖 AI-Powered Contributor Summaries & Profiles

- [Roadmap](#roadmap)*   💬 Natural Language Codebase Querying

- [Contributing](#contributing)*   📊 Repository & Contributor Exploration

- [License](#license)*   🎮 Gamification System (XP, Levels, Badges)

- [Team](#team)*   🔥 AI Burnout Detection & Work Pattern Analysis

*   🤝 Collaboration Network Visualization

---*   📈 Predictive Analytics & Health Metrics

*   👥 "Digital Twin" Interaction via Chat

## 🎯 Overview

## New! Dynamic Repository Import

**Katalyst** is an enterprise-grade developer analytics platform that connects to GitHub organizations to analyze repositories, contributors, and codebase activity. Using advanced AI ( /Gemini), it transforms raw GitHub data into actionable insights, helping organizations optimize team performance, prevent burnout, and accelerate development velocity.

Import any public GitHub repository instantly:

### What Makes Katalyst Different?- Enter repository URL (e.g., `facebook/react`)

- Automatic data fetching from GitHub

- 🤖 **AI-Native**: Every insight powered by  /Gemini AI- AI-powered analytics generated on import

- 📊 **DORA Metrics**: Industry-standard DevOps performance tracking- Real-time collaboration & burnout analysis

- 🔥 **Burnout Detection**: ML-powered work pattern analysis

- 💬 **Natural Language Queries**: Ask questions about your codebase in plain EnglishSee [IMPORT_GUIDE.md](IMPORT_GUIDE.md) for detailed instructions.

- 🎮 **Gamification**: XP, levels, badges to boost team engagement

- 🌐 **Collaboration Networks**: Visualize team interactions and knowledge silos## Tech Stack

- 🚀 **Real-time Sync**: GitHub App with webhook integration

*   **Backend:** Python (Django),   API

---*   **Frontend:** ReactJS, Vite, Tailwind CSS

*   **Data APIs:** GitHub API

## 🚨 The Problem*   **Real-time Conversation:** PlayAI API powered by Groq



In large organizations with multiple repositories and distributed teams:## Getting Started



- **Finding the Right Expert** takes hours of searching through commit logs1.  **Clone the repository:**

- **Code Knowledge** is siloed in individual contributors' minds    ```bash

- **Team Burnout** goes undetected until it's too late    git clone https://github.com/TheCl3m/ -hack

- **Contribution Patterns** remain invisible to management    cd  -hack

- **Onboarding New Developers** is slow due to lack of context    ```

- **Release Readiness** is guesswork without data-driven insights2.  **Set up Backend (Django):**

    ```bash

---    cd backend

    python -m venv venv

## 💡 Our Solution    source venv/bin/activate  # Use `.\venv\Scripts\activate` on Windows

    pip install -r requirements.txt

Katalyst addresses these challenges through:    # Create a .env file in this 'backend' directory

    # Add your API keys and Django secret key:

### 1. **Intelligent Repository Import**    #  LLAMA_API_KEY=your_ LLAMA_api_key

```    # Add any other necessary backend env vars (like DB config if not SQLite)

Enter GitHub URL → Fetch Data → AI Analysis → Instant Insights    python manage.py migrate # Run migrations if needed

```    python manage.py runserver

Import any public repository in seconds. Our AI automatically:    ```

- Identifies key contributors and their expertise areas    *The backend should now be running, typically on `http://127.0.0.1:8000/`.*

- Analyzes commit patterns and work rhythms

- Detects collaboration networks3.  **Set up Frontend:**

- Generates natural language summaries    *(In a separate terminal)*

    ```bash

### 2. **AI-Powered Contributor Profiles**    cd frontend

Each contributor gets an AI-generated profile including:    npm install

- Expertise areas (languages, frameworks, domains)    npm run dev

- Work patterns (preferred hours, commit frequency)    ```

- Burnout risk assessment    *The frontend development server should now be running, typically on `http://localhost:5173/` (check terminal output).*

- Collaboration strength

- Achievement badges and levels4.  **Access the App:** Open your browser to the frontend URL (e.g., `http://localhost:5173`).



### 3. **Digital Twin Chatbot**## Team

Interact with an AI representation of any contributor:

- Ask about their work on specific features*   Katalyst

- Understand their coding patterns*   Clement (TheCl3m) - [GitHub](https://github.com/TheCl3m)

- Get context before reaching out*   Karol (MrCogito) - [GitHub](https://github.com/MrCogito)

- Query codebase history naturally*   Jakob (TheDingodile) - [GitHub](https://github.com/TheDingodile)



### 4. **Team Health Dashboard**## Acknowledgements

Real-time visualization of:

- Code quality trends*   Powered by **Meta  **.

- Collaboration health*   Thanks to Cerebral Valley and Meta for the opportunity to build this project.

- Velocity metrics

- Documentation coverage## License

- Test coverage

- Burnout risk levelsThis project is licensed under CC BY-NC 4.0. No commercial use allowed without explicit permission.


---

## ✨ Key Features

### 🔍 **Analytics & Insights**

#### DORA Metrics
- **Deployment Frequency**: How often code ships to production
- **Lead Time for Changes**: Time from commit to deployment
- **Change Failure Rate**: Percentage of deployments causing failures
- **Mean Time to Recovery**: Average time to restore service

#### Team Health Radar
6-dimensional team performance analysis:
- Code Quality (complexity, maintainability)
- Collaboration (pair programming, reviews)
- Velocity (commits per sprint)
- Documentation (coverage, quality)
- Test Coverage (unit, integration, e2e)
- Burnout Risk (work patterns, stress indicators)

#### Release Readiness Score
AI-powered quality assessment:
- Code review completeness
- Test coverage percentage
- Documentation status
- Known bug severity
- Deployment risk level

### 🎮 **Gamification System**

- **Experience Points (XP)**: Earn XP for commits, issues, reviews
- **Levels**: Progress from level 1 to 100
- **Badges**: Achievements for milestones
  - 🔥 Hot Streak (7+ consecutive days)
  - 🐛 Bug Slayer (10+ bugs fixed)
  - 📚 Documentation Hero (50+ docs updated)
  - 🤝 Collaboration King (100+ PR reviews)
- **Leaderboards**: Team and organization rankings

### 🤖 **AI Features**

#### Auto-Triage Chatbot
Automatically classify and prioritize issues:
- Bug vs Feature detection
- Priority assignment (Critical/High/Medium/Low)
- Expertise matching (route to right developer)
- Duplicate detection

#### Sprint Planner AI
Intelligent sprint planning:
- Task estimation based on historical data
- Capacity planning per team member
- Dependency detection
- Velocity predictions
- Risk assessment

#### Natural Language Queries
Ask questions like:
- "Who is the expert on authentication?"
- "Which commits caused the performance regression?"
- "Show me all issues related to the payment module"
- "What did Sarah work on last sprint?"

### 🔄 **GitHub Integration**

#### GitHub App (Auto-Sync)
- One-click installation
- Automatic repository sync
- Real-time webhook updates
- Incremental data fetching
- Rate limit management

#### Supported Events
- Push (new commits)
- Pull Request (opened, merged, reviewed)
- Issues (created, closed, commented)
- Releases (published)

### 🔐 **Enterprise Features**

#### Multi-Tenancy
- Organization support
- Team management
- Repository access control

#### Role-Based Access Control (RBAC)
- **Owner**: Full control
- **Admin**: Manage members, repos
- **Member**: View and contribute
- **Viewer**: Read-only access

#### Audit Logging
- Track all actions
- Export compliance reports
- Retention policies

---

## 🛠️ Tech Stack

### Frontend
```json
{
  "framework": "React 19.0.0",
  "build": "Vite 6.3.1",
  "routing": "React Router DOM 7.5.3",
  "styling": "Tailwind CSS v4",
  "state": "TanStack React Query 5.75.1",
  "http": "Axios 1.9.0",
  "visualizations": [
    "React Force Graph (network graphs)",
    "React Flow (workflow diagrams)",
    "D3 Scale (data scaling)",
    "OGL (WebGL 3D effects)",
    "GSAP (animations)"
  ],
  "ui": [
    "Heroicons",
    "Headless UI",
    "Lucide React"
  ]
}
```

### Backend
```json
{
  "framework": "Django 5.2",
  "api": "Django REST Framework 3.16.0",
  "database": "PostgreSQL 14+",
  "authentication": "Django Simple JWT",
  "ai": [
    "  API (primary)",
    "Google Gemini (secondary)",
    "PlayAI + Groq (conversational)"
  ],
  "ml": [
    "NumPy",
    "Pandas",
    "Scikit-learn"
  ],
  "integrations": [
    "GitHub API",
    "GitHub App Webhooks"
  ]
}
```

### Infrastructure
- **Development**: PostgreSQL + Vite Dev Server
- **Production**: PostgreSQL + Nginx + Gunicorn
- **Deployment**: Docker-ready (containers coming soon)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React 19)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │Analytics │  │Contributors│  │Chatbot  │   │
│  └────┬─────┘  └────┬─────┘  └─────┬──────┘  └────┬────┘   │
│       │             │              │               │        │
│       └─────────────┴──────────────┴───────────────┘        │
│                          │                                   │
│                    React Query                               │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │ REST API
┌──────────────────────────┼───────────────────────────────────┐
│                          ▼                                   │
│              Django REST Framework                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           API Views & Serializers                    │   │
│  └───────────────────┬──────────────────────────────────┘   │
│                      │                                       │
│  ┌───────────────────┼──────────────────┐                   │
│  │  Business Logic Layer                │                   │
│  │  ┌──────────┐  ┌─────────┐  ┌──────┐│                   │
│  │  │ GitHub   │  │   AI    │  │Analytics││                 │
│  │  │ Importer │  │ Engine  │  │Engine ││                  │
│  │  └────┬─────┘  └────┬────┘  └───┬──┘│                   │
│  │       │             │            │   │                   │
│  └───────┼─────────────┼────────────┼───┘                   │
│          │             │            │                       │
│  ┌───────▼─────────────▼────────────▼─────────┐             │
│  │         Django ORM (Models)                │             │
│  └───────────────────┬────────────────────────┘             │
│                      │                                       │
│  ┌───────────────────▼────────────────────────┐             │
│  │         SQLite Database                    │             │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │             │
│  │  │Repository│  │Contributor│  │  Commit  │ │             │
│  │  │   Work   │  │   Issue   │  │Analytics │ │             │
│  │  └──────────┘  └──────────┘  └──────────┘ │             │
│  └────────────────────────────────────────────┘             │
└──────────────────────────────────────────────────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
┌─────────┐          ┌──────────┐          ┌──────────┐
│ GitHub  │          │      │          │ Gemini   │
│   API   │          │   API    │          │   API    │
└─────────┘          └──────────┘          └──────────┘
```

### Data Flow

1. **Import Flow**
```
User enters GitHub URL
    ↓
Frontend validates & sends to API
    ↓
GitHubFetcher pulls data (repos, commits, issues)
    ↓
GitHubImporter transforms & saves to database
    ↓
AI Engine generates summaries (async)
    ↓
Analytics Engine calculates metrics
    ↓
Frontend polls for completion & displays results
```

2. **Real-time Sync Flow** (GitHub App)
```
GitHub Event (push, PR, issue)
    ↓
Webhook hits /api/webhooks/github/
    ↓
Event validated & queued
    ↓
Sync Manager processes incrementally
    ↓
Database updated
    ↓
Frontend receives update via React Query invalidation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.9 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **PostgreSQL**: 14.x or higher
- **Git**: Latest version

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/riyamittal12426/LazySheeps.git
cd LazySheeps
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL database
# Open psql or pgAdmin and run:
# CREATE DATABASE katalyst_db;
# CREATE USER katalyst_user WITH PASSWORD 'your_password';
# GRANT ALL PRIVILEGES ON DATABASE katalyst_db TO katalyst_user;

# Create environment file
# Create a .env file in the backend directory with:
```

**`.env` file contents:**
```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database
DB_NAME=katalyst_db
DB_USER=katalyst_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# AI APIs
 LLAMA_API_KEY=your- -api-key
GEMINI_API_KEY=your-gemini-api-key

# GitHub
GITHUB_TOKEN=your-github-token
GITHUB_APP_ID=your-app-id
GITHUB_APP_PRIVATE_KEY=your-private-key
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# Database (optional, defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost:5432/katalyst
```

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Backend will run on `http://127.0.0.1:8000/`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:5173/`

### Quick Start Guide

1. **Access the Application**
   - Open browser to `http://localhost:5173/`
   - Landing page will appear

2. **Import Your First Repository**
   - Click "Get Started" → Dashboard
   - Enter a GitHub URL (e.g., `facebook/react`)
   - Click "Import Repository"
   - Wait for AI analysis to complete (~30 seconds)

3. **Explore Analytics**
   - View contributor profiles
   - Check commit timelines
   - Analyze team health
   - Ask questions via chatbot

---

## 🎨 Features Deep Dive

### 1. Repository Import

**How it works:**
1. User enters GitHub repository URL
2. System validates URL format
3. GitHub API fetches:
   - Repository metadata
   - Contributors list
   - Commits (up to 500)
   - Issues (up to 500)
4. Data is transformed and saved
5. AI generates summaries for:
   - Repository overview
   - Each contributor
   - Each repository work (contributor-repo relationship)
6. Analytics engine calculates:
   - DORA metrics
   - Collaboration networks
   - Burnout risk scores

**Supported Repositories:**
- ✅ Public repositories
- ✅ Private repositories (with token)
- ✅ Organization repositories
- ✅ Multi-repository import

### 2. Contributor Analytics

**Profile Components:**

**Basic Info:**
- Username, avatar, GitHub profile link
- Total commits, issues, PRs reviewed
- Join date, last activity

**AI-Generated Summary:**
```
Example:
"Sarah is a full-stack developer with deep expertise in React and 
Node.js. She primarily works on frontend components and API 
integration. Known for thorough code reviews and clear 
documentation. Most active during US East Coast hours (9 AM - 6 PM 
EST). Consistent contributor with low burnout risk."
```

**Work Patterns:**
- Preferred work hours (ML-detected)
- Commit frequency (daily, weekly trends)
- Activity streak (consecutive days)
- Code churn ratio (deletions/additions)

**Collaboration:**
- Top collaborators (by co-commits)
- Review participation
- Issue discussions
- Knowledge sharing score

**Gamification:**
- Current level (1-100)
- Experience points
- Earned badges
- Leaderboard rank

### 3. DORA Metrics Dashboard

**Deployment Frequency**
```
How often: Daily | Weekly | Monthly | Yearly

Chart: Line graph showing deployments over time
Target: Elite = Multiple per day
        High = Weekly to monthly
        Medium = Monthly to every 6 months
        Low = Less than every 6 months
```

**Lead Time for Changes**
```
Time: < 1 hour | < 1 day | < 1 week | > 1 week

Calculation: Time from first commit to production
Target: Elite = Less than 1 hour
        High = Less than 1 day
        Medium = Less than 1 week
        Low = More than 1 week
```

**Change Failure Rate**
```
Percentage: 0-15% | 16-30% | 31-45% | > 45%

Calculation: Failed deployments / Total deployments
Target: Elite = 0-15%
        High = 16-30%
        Medium = 31-45%
        Low = > 45%
```

**Mean Time to Recovery**
```
Time: < 1 hour | < 1 day | < 1 week | > 1 week

Calculation: Average time to restore service after failure
Target: Elite = Less than 1 hour
        High = Less than 1 day
        Medium = Less than 1 week
        Low = More than 1 week
```

### 4. Auto-Triage Chatbot

**Issue Classification:**

Input: New issue text
Output:
```json
{
  "type": "bug" | "feature" | "documentation" | "question",
  "priority": "critical" | "high" | "medium" | "low",
  "suggested_assignee": "username",
  "estimated_effort": "1-3 hours" | "3-8 hours" | "1-3 days" | "1+ weeks",
  "related_issues": [123, 456],
  "affected_components": ["auth", "payment"],
  "confidence": 0.87
}
```

**Example:**
```
Issue: "Login fails with 500 error when using OAuth"

AI Analysis:
✓ Type: Bug (98% confidence)
✓ Priority: High (critical path affected)
✓ Assign to: @sarah-auth-expert
✓ Effort: 3-8 hours
✓ Related: Issue #234 (OAuth integration)
✓ Components: auth, oauth, backend
```

### 5. Sprint Planner AI

**Intelligent Task Allocation:**

Input:
- Available team members
- Sprint duration (2 weeks)
- Backlog items

Output:
- Optimized task distribution
- Velocity prediction
- Risk assessment
- Dependency warnings

**Example Sprint Plan:**
```
Sprint 12 (Dec 1 - Dec 14)

Sarah (Senior Frontend) - 40 points
  ✓ Redesign dashboard UI (13 pts)
  ✓ Implement dark mode (8 pts)
  ✓ Fix mobile responsiveness (8 pts)
  ✓ Code review budget (11 pts)

Mike (Backend Lead) - 35 points
  ✓ API performance optimization (13 pts)
  ✓ Database migration (8 pts)
  ✓ Security audit (5 pts)
  ✓ Team support (9 pts)

Predicted Velocity: 75 points
Confidence: 87%
Risks: Sarah has 2 days PTO (accounted for)
```

### 6. Team Health Radar

**6 Dimensions:**

1. **Code Quality** (0-100)
   - Cyclomatic complexity
   - Code duplication
   - Maintainability index
   - Technical debt ratio

2. **Collaboration** (0-100)
   - PR review participation
   - Pair programming frequency
   - Knowledge sharing
   - Silo risk

3. **Velocity** (0-100)
   - Commits per sprint
   - Story points completed
   - Trend (increasing/decreasing)
   - Consistency

4. **Documentation** (0-100)
   - README completeness
   - API documentation
   - Code comments
   - Architecture diagrams

5. **Test Coverage** (0-100)
   - Unit test %
   - Integration test %
   - E2E test %
   - Test quality

6. **Burnout Risk** (0-100, lower is better)
   - Work hours pattern
   - Weekend activity
   - Vacation usage
   - Stress indicators

**Visualization:**
```
         Code Quality
              100
               |
   Documentation --+-- Collaboration
               |  |  |
              50  |  |
               |  |  |
Test Coverage  +--+--+ Velocity
               |     |
               0     |
                     |
                Burnout Risk
                (inverted scale)
```

---

## 📡 API Documentation

### Base URL
```
Development: http://127.0.0.1:8000/api/
Production: https://api.katalyst.dev/api/
```

### Authentication
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Use access token in subsequent requests:
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Repository Endpoints

#### Import Repository
```http
POST /api/repositories/import/
Content-Type: application/json

{
  "repo_url": "https://github.com/facebook/react"
}

Response:
{
  "id": 123,
  "name": "react",
  "full_name": "facebook/react",
  "status": "importing",
  "message": "Import started. Check status endpoint for progress."
}
```

#### List Repositories
```http
GET /api/repositories/

Response:
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "react",
      "full_name": "facebook/react",
      "description": "The library for web and native user interfaces",
      "language": "JavaScript",
      "stars_count": 227000,
      "forks_count": 46000,
      "contributors_count": 1500,
      "commits_count": 15234,
      "last_synced_at": "2025-11-09T12:00:00Z"
    }
  ]
}
```

#### Repository Details
```http
GET /api/repositories/{id}/

Response:
{
  "id": 1,
  "name": "react",
  "full_name": "facebook/react",
  "url": "https://github.com/facebook/react",
  "description": "...",
  "summary": "AI-generated repository overview...",
  "language": "JavaScript",
  "stats": {
    "commits": 15234,
    "contributors": 1500,
    "issues": 2341,
    "pull_requests": 4567
  },
  "dora_metrics": {
    "deployment_frequency": "daily",
    "lead_time_hours": 12.5,
    "change_failure_rate": 0.08,
    "mttr_hours": 2.3
  }
}
```

### Contributor Endpoints

#### List Contributors
```http
GET /api/contributors/?page=1&page_size=20

Response:
{
  "count": 1500,
  "next": "/api/contributors/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "gaearon",
      "avatar_url": "https://avatars.githubusercontent.com/u/810438",
      "total_commits": 2341,
      "total_issues_closed": 156,
      "level": 45,
      "experience_points": 23450,
      "burnout_risk_level": "low"
    }
  ]
}
```

#### Contributor Details
```http
GET /api/contributors/{id}/

Response:
{
  "id": 1,
  "username": "gaearon",
  "url": "https://github.com/gaearon",
  "avatar_url": "...",
  "summary": "AI-generated profile summary...",
  "stats": {
    "total_commits": 2341,
    "total_issues_closed": 156,
    "total_prs_reviewed": 543,
    "repositories_count": 23
  },
  "work_patterns": {
    "preferred_work_hours": "9 AM - 6 PM EST",
    "activity_streak": 127,
    "burnout_risk_level": "low",
    "avg_commit_size": 145.3,
    "collaboration_score": 8.7
  },
  "gamification": {
    "level": 45,
    "experience_points": 23450,
    "badges": [
      {"name": "Hot Streak", "icon": "🔥"},
      {"name": "Code Reviewer", "icon": "👁️"}
    ]
  },
  "repositories": [...]
}
```

### Analytics Endpoints

#### DORA Metrics
```http
GET /api/analytics/dora/?repository_id=1

Response:
{
  "repository_id": 1,
  "period": "last_30_days",
  "metrics": {
    "deployment_frequency": {
      "value": "daily",
      "count": 45,
      "rating": "elite"
    },
    "lead_time_for_changes": {
      "average_hours": 12.5,
      "rating": "high"
    },
    "change_failure_rate": {
      "percentage": 8,
      "rating": "elite"
    },
    "mean_time_to_recovery": {
      "average_hours": 2.3,
      "rating": "elite"
    }
  }
}
```

#### Team Health
```http
GET /api/analytics/team-health/?repository_id=1

Response:
{
  "repository_id": 1,
  "dimensions": {
    "code_quality": 85,
    "collaboration": 78,
    "velocity": 92,
    "documentation": 65,
    "test_coverage": 71,
    "burnout_risk": 23
  },
  "overall_health": 78.5,
  "trends": {
    "code_quality": "+5",
    "collaboration": "-2",
    "velocity": "+8"
  }
}
```

#### Collaboration Network
```http
GET /api/analytics/collaboration/?repository_id=1

Response:
{
  "nodes": [
    {"id": "user1", "name": "Sarah", "commits": 234},
    {"id": "user2", "name": "Mike", "commits": 189}
  ],
  "links": [
    {"source": "user1", "target": "user2", "weight": 45}
  ]
}
```

### AI Endpoints

#### Chat with AI
```http
POST /api/ai/chat/
Content-Type: application/json

{
  "message": "Who is the expert on authentication?",
  "context": {
    "repository_id": 1
  }
}

Response:
{
  "reply": "Based on commit history, Sarah (@sarah-dev) is the primary expert on authentication. She authored 78% of commits in the auth module and has deep expertise in OAuth, JWT, and security best practices.",
  "confidence": 0.92,
  "sources": [
    {"type": "commit", "id": 1234},
    {"type": "contributor", "id": 5}
  ]
}
```

#### Auto-Triage Issue
```http
POST /api/ai/triage-issue/
Content-Type: application/json

{
  "title": "Login fails with 500 error",
  "body": "When using OAuth login, server returns 500...",
  "repository_id": 1
}

Response:
{
  "type": "bug",
  "priority": "high",
  "suggested_assignee": "sarah-dev",
  "estimated_effort": "3-8 hours",
  "affected_components": ["auth", "oauth"],
  "confidence": 0.89
}
```

### Webhook Endpoint

```http
POST /api/webhooks/github/
X-GitHub-Event: push
X-Hub-Signature-256: sha256=...

{
  "repository": {
    "full_name": "facebook/react"
  },
  "commits": [...]
}

Response:
{
  "status": "received",
  "processed": true
}
```

---

## 🗄️ Database Schema

### Core Tables

#### Repository
```sql
CREATE TABLE repository (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    full_name VARCHAR(255) UNIQUE,
    url TEXT,
    github_id INTEGER UNIQUE,
    description TEXT,
    language VARCHAR(50),
    stars_count INTEGER DEFAULT 0,
    forks_count INTEGER DEFAULT 0,
    organization_id INTEGER REFERENCES organization(id),
    installation_id INTEGER REFERENCES github_app_installation(id),
    last_synced_at TIMESTAMP,
    auto_sync_enabled BOOLEAN DEFAULT FALSE,
    webhook_configured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Contributor
```sql
CREATE TABLE contributor (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    url TEXT,
    avatar_url TEXT,
    summary TEXT,
    total_commits INTEGER DEFAULT 0,
    total_issues_closed INTEGER DEFAULT 0,
    total_prs_reviewed INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    experience_points INTEGER DEFAULT 0,
    preferred_work_hours VARCHAR(50),
    activity_streak INTEGER DEFAULT 0,
    burnout_risk_level VARCHAR(20),
    avg_commit_size REAL DEFAULT 0,
    collaboration_score REAL DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### RepositoryWork (Junction)
```sql
CREATE TABLE repository_work (
    id INTEGER PRIMARY KEY,
    repository_id INTEGER REFERENCES repository(id),
    contributor_id INTEGER REFERENCES contributor(id),
    summary TEXT,
    commit_count INTEGER DEFAULT 0,
    issue_count INTEGER DEFAULT 0,
    lines_added INTEGER DEFAULT 0,
    lines_removed INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(repository_id, contributor_id)
);
```

#### Commit
```sql
CREATE TABLE commit (
    id INTEGER PRIMARY KEY,
    work_id INTEGER REFERENCES repository_work(id),
    repository_id INTEGER REFERENCES repository(id),
    contributor_id INTEGER REFERENCES contributor(id),
    sha VARCHAR(40) UNIQUE,
    message TEXT,
    url TEXT,
    raw_data JSON,
    summary TEXT,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    code_churn_ratio REAL DEFAULT 0,
    committed_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Issue
```sql
CREATE TABLE issue (
    id INTEGER PRIMARY KEY,
    work_id INTEGER REFERENCES repository_work(id),
    github_issue_id INTEGER UNIQUE,
    number INTEGER,
    title VARCHAR(500),
    body TEXT,
    url TEXT,
    raw_data JSON,
    summary TEXT,
    state VARCHAR(20) DEFAULT 'open',
    is_bug BOOLEAN DEFAULT FALSE,
    is_feature BOOLEAN DEFAULT FALSE,
    priority VARCHAR(20) DEFAULT 'medium',
    closed_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Relationships

```
Organization (1) ←→ (N) Repository
Organization (1) ←→ (N) Team
Team (1) ←→ (N) TeamMember
Repository (1) ←→ (N) RepositoryWork ←→ (N) Contributor
RepositoryWork (1) ←→ (N) Commit
RepositoryWork (1) ←→ (N) Issue
Contributor (1) ←→ (N) ActivityLog
Contributor (N) ←→ (N) Contributor (Collaboration)
Contributor (N) ←→ (N) Badge
```

### Indexes

```sql
CREATE INDEX idx_commit_sha ON commit(sha);
CREATE INDEX idx_commit_contributor ON commit(contributor_id, committed_at DESC);
CREATE INDEX idx_issue_github_id ON issue(github_issue_id);
CREATE INDEX idx_activity_contributor ON activity_log(contributor_id, timestamp DESC);
CREATE INDEX idx_repository_org ON repository(organization_id);
```

---

## 📸 Screenshots

### Landing Page
![Landing Page](images/landing.png)
*Modern landing page with animated hero section and feature showcase*

### Dashboard
![Dashboard](images/dashboard.png)
*Overview of repositories, contributors, and key metrics*

### Contributor Profile
![Contributor Profile](images/contributor-profile.png)
*AI-generated profile with work patterns and collaboration network*

### Team Health Radar
![Team Health](images/team-health.png)
*6-dimensional team performance visualization*

### DORA Metrics
![DORA Metrics](images/dora-metrics.png)
*Industry-standard DevOps performance tracking*

---

## 🗺️ Roadmap

### Q4 2025
- [x] Core repository import
- [x] AI-powered summaries ( /Gemini)
- [x] DORA metrics dashboard
- [x] Team health radar
- [x] Gamification system
- [x] Auto-triage chatbot
- [ ] Docker deployment
- [ ] PostgreSQL migration

### Q1 2026
- [ ] GitHub App marketplace listing
- [ ] Slack integration
- [ ] Email notifications
- [ ] Custom dashboards
- [ ] Export reports (PDF/CSV)
- [ ] Private repository support
- [ ] SSO authentication

### Q2 2026
- [ ] Jira integration
- [ ] GitLab support
- [ ] Bitbucket support
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Video tutorials

### Q3 2026
- [ ] Enterprise on-premise deployment
- [ ] Custom ML models
- [ ] Advanced security features
- [ ] Compliance certifications (SOC2, ISO)
- [ ] Multi-language support
- [ ] API v2

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write tests
5. Run linters (`npm run lint`, `flake8`)
6. Commit (`git commit -m 'Add amazing feature'`)
7. Push (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- **Frontend**: ESLint + Prettier
- **Backend**: Black + Flake8
- **Commits**: Conventional Commits

---

## 📄 License

This project is licensed under **CC BY-NC 4.0** (Creative Commons Attribution-NonCommercial 4.0 International).

**You are free to:**
- ✅ Share — copy and redistribute the material
- ✅ Adapt — remix, transform, and build upon the material

**Under the following terms:**
- 📝 **Attribution** — You must give appropriate credit
- 🚫 **NonCommercial** — You may not use the material for commercial purposes

For commercial use, please contact: [riyamittal12426@gmail.com](mailto:riyamittal12426@gmail.com)

Full license: https://creativecommons.org/licenses/by-nc/4.0/

---

## 👥 Team

**LazySheeps** 🐑

- **Riya Mittal** - Lead Developer - [@riyamittal12426](https://github.com/riyamittal12426)

Built with ❤️ for HackCBS Hackathon 2025

---

## 🙏 Acknowledgements

- **Meta  ** - AI-powered insights
- **Google Gemini** - Alternative AI provider
- **GitHub API** - Repository data
- **React Team** - Amazing frontend framework
- **Django Team** - Robust backend framework
- **HackCBS** - Hackathon opportunity

---

## 📞 Contact

- **Email**: riyamittal12426@gmail.com
- **GitHub**: [@riyamittal12426](https://github.com/riyamittal12426)
- **Repository**: [github.com/riyamittal12426/LazySheeps](https://github.com/riyamittal12426/LazySheeps)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with 💜 by LazySheeps

</div>
