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
    import_github_repository, import_status, sync_repository, delete_repository,
    commit_analytics, commit_timeline, contributor_commit_summaries,
    register, login, logout, get_profile, update_profile, get_user_stats
)
from api.dora_views import repository_dora_metrics, calculate_all_dora_metrics
from api.webhooks import github_webhook, webhook_health
from api.github_auth import github_auth_url, github_callback, github_repositories, import_repositories
from api.triage_chatbot_views import (
    auto_triage_issue, classify_issue, detect_duplicate_issue, suggest_assignee,
    chatbot_command, pr_summary, team_health, daily_digest, risk_alerts,
    slack_webhook, discord_webhook
)
from api.github_app import (
    github_app_manifest, github_app_install_url, github_app_callback,
    list_installations, installation_repositories, bulk_import_repositories,
    github_app_webhook, delete_installation
)
from api.webhook_views import (
    github_webhook_handler, trigger_periodic_sync, sync_repository_endpoint,
    sync_jobs_list, webhook_health_check
)
from api.team_health import team_health_radar, contributor_health_detail
from api.live_stream import live_event_stream
from api.git_server import (
    git_http_backend, create_repository, browse_repository, get_file,
    repository_commits, post_receive_webhook, list_user_repositories
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
    
    # GitHub App Integration (Enterprise-grade)
    path('api/github-app/manifest/', github_app_manifest, name='github_app_manifest'),
    path('api/github-app/install-url/', github_app_install_url, name='github_app_install_url'),
    path('api/github-app/callback/', github_app_callback, name='github_app_callback'),
    path('api/github-app/installations/', list_installations, name='list_installations'),
    path('api/github-app/installations/<int:installation_id>/repositories/', installation_repositories, name='installation_repositories'),
    path('api/github-app/installations/<int:installation_id>/bulk-import/', bulk_import_repositories, name='bulk_import_repositories'),
    path('api/github-app/installations/<int:installation_id>/delete/', delete_installation, name='delete_installation'),
    path('api/github-app/webhook/', github_app_webhook, name='github_app_webhook'),
    
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
    path('api/repositories/<int:repo_id>/delete/', delete_repository, name='delete_repository'),
    
    # Commit Analytics
    path('api/commits/analytics/', commit_analytics, name='commit_analytics'),
    path('api/commits/timeline/', commit_timeline, name='commit_timeline'),
    path('api/commits/contributor-summaries/', contributor_commit_summaries, name='contributor_commit_summaries'),
    
    # GitHub Webhooks (Old - kept for backward compatibility)
    path('api/webhooks/github/', github_webhook, name='github_webhook'),
    path('api/webhooks/health/', webhook_health, name='webhook_health'),
    path('api/webhooks/slack/', slack_webhook, name='slack_webhook'),
    path('api/webhooks/discord/', discord_webhook, name='discord_webhook'),
    
    # Auto-Triage & Issue Management
    path('api/triage/issue/', auto_triage_issue, name='auto_triage_issue'),
    path('api/triage/classify/', classify_issue, name='classify_issue'),
    path('api/triage/detect-duplicate/', detect_duplicate_issue, name='detect_duplicate_issue'),
    path('api/triage/suggest-assignee/<int:repository_id>/', suggest_assignee, name='suggest_assignee'),
    
    # ChatBot (Slack/Discord)
    path('api/chatbot/command/', chatbot_command, name='chatbot_command'),
    path('api/chatbot/pr-summary/', pr_summary, name='pr_summary'),
    path('api/chatbot/team-health/', team_health, name='team_health'),
    path('api/chatbot/daily-digest/', daily_digest, name='daily_digest'),
    path('api/chatbot/risk-alerts/', risk_alerts, name='risk_alerts'),
    
    # GitHub Auto-Sync System (New Enterprise-Grade)
    path('api/github/webhook/', github_webhook_handler, name='github_webhook_handler'),
    path('api/sync/periodic/', trigger_periodic_sync, name='trigger_periodic_sync'),
    path('api/sync/repository/<int:repo_id>/', sync_repository_endpoint, name='sync_repository_endpoint'),
    path('api/sync/jobs/', sync_jobs_list, name='sync_jobs_list'),
    path('api/sync/health/', webhook_health_check, name='webhook_health_check'),
    
    # DORA Metrics
    path('api/repositories/<int:repo_id>/dora/', repository_dora_metrics, name='repository_dora'),
    path('api/dora/calculate-all/', calculate_all_dora_metrics, name='calculate_all_dora'),
    
    # Team Health Radar
    path('api/team-health/', team_health_radar, name='team_health_radar'),
    path('api/team-health/<int:contributor_id>/', contributor_health_detail, name='contributor_health_detail'),
    
    # Live Activity Stream (SSE)
    path('api/events/stream/', live_event_stream, name='live_event_stream'),
    
    # Local Git Server (Self-hosted repositories)
    path('api/git/create/', create_repository, name='create_git_repository'),
    path('api/git/<str:username>/<str:repo_name>/browse/', browse_repository, name='browse_repository'),
    path('api/git/<str:username>/<str:repo_name>/file/', get_file, name='get_file'),
    path('api/git/<str:username>/<str:repo_name>/commits/', repository_commits, name='repository_commits'),
    path('api/git/<str:username>/repositories/', list_user_repositories, name='list_user_repositories'),
    path('api/git/webhook/post-receive/', post_receive_webhook, name='post_receive_webhook'),
    
    # Git HTTP Backend (Smart Protocol for push/pull)
    path('git/<str:username>/<str:repo_name>/info/refs', git_http_backend, {'service': 'info'}, name='git_info_refs'),
    path('git/<str:username>/<str:repo_name>/git-upload-pack', git_http_backend, {'service': 'git-upload-pack'}, name='git_upload_pack'),
    path('git/<str:username>/<str:repo_name>/git-receive-pack', git_http_backend, {'service': 'git-receive-pack'}, name='git_receive_pack'),
]
