"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api.views import (
    get_data, llm_stream_view,
    leaderboard, contributor_stats, award_badges, predict_burnout,
    repository_health, predict_completion,
    collaboration_network, collaboration_patterns,
    dashboard_stats, activity_trends, search_contributors,
    import_github_repository, import_status, sync_repository,
    commit_analytics, commit_timeline, contributor_commit_summaries,
    register, login, logout, get_profile, update_profile, get_user_stats
)
from api.sprint_views import (
    suggest_sprint_plan, create_sprint, get_sprint, list_sprints,
    update_sprint, delete_sprint, add_issue_to_sprint, update_sprint_issue,
    sprint_velocity_trends, team_capacity_analysis, forecast_completion,
    complete_sprint
)
from api.dora_views import repository_dora_metrics, calculate_all_dora_metrics
from api.webhooks import github_webhook, webhook_health
from api.github_auth import github_auth_url, github_callback, github_repositories, import_repositories
from api.release_views import (
    get_release_readiness, get_release_readiness_score_only, get_release_blockers,
    get_readiness_trend, compare_repositories_readiness, get_all_repositories_readiness,
    get_readiness_dashboard
)
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from api.rbac_views import OrganizationViewSet, TeamViewSet, AuditLogViewSet

# Create router for RBAC ViewSets
router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # RBAC API (Organizations, Teams, Audit Logs)
    path('api/', include(router.urls)),
    
    # Authentication
    path('api/auth/register/', register, name='register'),
    path('api/auth/login/', login, name='login'),
    path('api/auth/logout/', logout, name='logout'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', get_profile, name='get_profile'),
    path('api/auth/profile/update/', update_profile, name='update_profile'),
    path('api/auth/stats/', get_user_stats, name='get_user_stats'),
    
    # GitHub OAuth
    path('api/auth/github/url/', github_auth_url, name='github_auth_url'),
    path('api/auth/github/callback/', github_callback, name='github_callback'),
    path('api/github/repositories/', github_repositories, name='github_repositories'),
    path('api/github/import/', import_repositories, name='import_repositories'),
    
    # Original endpoints
    path('api/get_data/', get_data, name='get_data'),
    path('api/llm_stream/', llm_stream_view, name='llm_stream'),
    
    # Gamification & Leaderboard
    path('api/leaderboard/', leaderboard, name='leaderboard'),
    path('api/contributors/<int:contributor_id>/stats/', contributor_stats, name='contributor_stats'),
    path('api/contributors/<int:contributor_id>/badges/', award_badges, name='award_badges'),
    path('api/contributors/<int:contributor_id>/burnout/', predict_burnout, name='predict_burnout'),
    
    # Repository Analytics
    path('api/repositories/<int:repo_id>/health/', repository_health, name='repository_health'),
    path('api/repositories/<int:repo_id>/predict-completion/', predict_completion, name='predict_completion'),
    
    # Collaboration Network
    path('api/collaboration/network/', collaboration_network, name='collaboration_network'),
    path('api/repositories/<int:repo_id>/collaboration/', collaboration_patterns, name='collaboration_patterns'),
    
    # Dashboard
    path('api/dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    path('api/dashboard/trends/', activity_trends, name='activity_trends'),
    
    # Search
    path('api/search/contributors/', search_contributors, name='search_contributors'),
    
    # GitHub Import & Sync
    path('api/repositories/import/', import_github_repository, name='import_github_repository'),
    path('api/repositories/import-status/', import_status, name='import_status'),
    path('api/repositories/<int:repo_id>/sync/', sync_repository, name='sync_repository'),
    
    # Commit Analytics
    path('api/commits/analytics/', commit_analytics, name='commit_analytics'),
    path('api/commits/timeline/', commit_timeline, name='commit_timeline'),
    path('api/commits/contributor-summaries/', contributor_commit_summaries, name='contributor_commit_summaries'),
    
    # GitHub Webhooks
    path('api/webhooks/github/', github_webhook, name='github_webhook'),
    path('api/webhooks/health/', webhook_health, name='webhook_health'),
    
    # DORA Metrics
    path('api/repositories/<int:repo_id>/dora/', repository_dora_metrics, name='repository_dora'),
    path('api/dora/calculate-all/', calculate_all_dora_metrics, name='calculate_all_dora'),
    
    # ============================================
    # SPRINT PLANNING AI
    # ============================================
    
    # AI Sprint Suggestion (Main Feature)
    path('api/sprints/suggest/', suggest_sprint_plan, name='suggest_sprint_plan'),
    
    # Sprint CRUD
    path('api/sprints/', create_sprint, name='create_sprint'),
    path('api/sprints/list/', list_sprints, name='list_sprints'),
    path('api/sprints/<int:sprint_id>/', get_sprint, name='get_sprint'),
    path('api/sprints/<int:sprint_id>/update/', update_sprint, name='update_sprint'),
    path('api/sprints/<int:sprint_id>/delete/', delete_sprint, name='delete_sprint'),
    path('api/sprints/<int:sprint_id>/complete/', complete_sprint, name='complete_sprint'),
    
    # Sprint Issues
    path('api/sprints/<int:sprint_id>/issues/', add_issue_to_sprint, name='add_issue_to_sprint'),
    path('api/sprints/<int:sprint_id>/issues/<int:issue_id>/', update_sprint_issue, name='update_sprint_issue'),
    
    # Sprint Analytics
    path('api/sprints/velocity/<int:repository_id>/', sprint_velocity_trends, name='sprint_velocity_trends'),
    path('api/sprints/capacity/', team_capacity_analysis, name='team_capacity_analysis'),
    path('api/sprints/forecast/<int:repository_id>/', forecast_completion, name='forecast_completion'),
    
    # ============================================
    # RELEASE READINESS SCORE
    # ============================================
    
    # Full Release Readiness Report
    path('api/release-readiness/<int:repo_id>/', get_release_readiness, name='get_release_readiness'),
    
    # Lightweight Score Only
    path('api/release-readiness/<int:repo_id>/score/', get_release_readiness_score_only, name='get_readiness_score_only'),
    
    # Blockers & Warnings
    path('api/release-readiness/<int:repo_id>/blockers/', get_release_blockers, name='get_release_blockers'),
    
    # Trend Analysis
    path('api/release-readiness/<int:repo_id>/trend/', get_readiness_trend, name='get_readiness_trend'),
    
    # Dashboard View
    path('api/release-readiness/<int:repo_id>/dashboard/', get_readiness_dashboard, name='get_readiness_dashboard'),
    
    # Multi-Repository Views
    path('api/release-readiness/all/', get_all_repositories_readiness, name='get_all_repositories_readiness'),
    path('api/release-readiness/compare/', compare_repositories_readiness, name='compare_repositories_readiness'),
]
