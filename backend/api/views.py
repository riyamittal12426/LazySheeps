import os
import time # Optional: for slight delay if needed during testing
from django.http import StreamingHttpResponse, JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import google.generativeai as genai
from django.conf import settings
from django.db.models import Q, Count, Avg, Sum
from .models import *
from .serializers import (
    DataSerializer, UserSerializer, RegisterSerializer, 
    LoginSerializer, UserProfileUpdateSerializer
)
from .analytics import ContributorAnalytics, RepositoryAnalytics, CollaborationAnalytics

# Configure Gemini API
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    # Use gemini-1.5-flash for free tier (15 RPM vs gemini-2.5-pro's 2 RPM)
    gemini_model = genai.GenerativeModel('gemini-2.5-pro')
    if settings.GEMINI_API_KEY:
        print(f"✓ Gemini API client initialized successfully (gemini-1.5-flash)")
        print(f"  API Key prefix: {settings.GEMINI_API_KEY[:20]}...")
    else:
        print("✗ GEMINI_API_KEY is not set in environment variables")
        gemini_model = None
except Exception as e:
    print(f"✗ Error initializing Gemini client: {e}")
    gemini_model = None


# --- Authentication Views ---

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user and return JWT tokens"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user by blacklisting refresh token"""
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'user': serializer.data
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': UserSerializer(request.user).data
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """Get user statistics"""
    user = request.user
    
    # Calculate user stats based on GitHub imports
    repositories = Repository.objects.filter(
        works__contributor__github_username=user.github_username
    ).distinct() if user.github_username else Repository.objects.none()
    
    commits = Commit.objects.filter(
        contributor__github_username=user.github_username
    ) if user.github_username else Commit.objects.none()
    
    stats = {
        'total_repositories': repositories.count(),
        'total_commits': commits.count(),
        'total_additions': commits.aggregate(Sum('additions'))['additions__sum'] or 0,
        'total_deletions': commits.aggregate(Sum('deletions'))['deletions__sum'] or 0,
        'average_commit_size': commits.aggregate(Avg('files_changed'))['files_changed__avg'] or 0,
        'repositories': [
            {
                'id': repo.id,
                'name': repo.name,
                'url': repo.url,
                'stars': repo.stars,
                'commits_count': commits.filter(repository=repo).count()
            }
            for repo in repositories[:10]  # Top 10 repositories
        ]
    }
    
    # Update user model stats
    user.total_repositories = stats['total_repositories']
    user.total_commits = stats['total_commits']
    user.total_contributions = stats['total_additions'] + stats['total_deletions']
    user.save()
    
    return Response({
        'success': True,
        'stats': stats
    })


# --- Simple Test View ---
@api_view(['GET'])
def get_data(request):
    """
    A simple endpoint to return the data.
    """
    try:
        print("get_data endpoint called")
        data = DataSerializer()
        print("DataSerializer instantiated")
        data = data.to_representation(data)
        print(f"Data serialized - Repos: {len(data.get('repositories', []))}, Contributors: {len(data.get('contributors', []))}")
        return Response(data)
    except Exception as e:
        print(f"Error in get_data: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)


# --- LLM Streaming View ---

def generate_gemini_stream(system_prompt, user_prompt):
    """
    Generator function to stream responses from Gemini API.
    Yields chunks of text content.
    """
    if not gemini_model:
        yield "Error: Gemini client not initialized. Check API key."
        return
    if not system_prompt or not user_prompt:
        yield "Error: No prompt provided."
        return

    try:
        # Combine system and user prompts for Gemini
        full_prompt = f"{system_prompt}\n\nUser Query: {user_prompt}"
        
        # Generate response with streaming
        response = gemini_model.generate_content(
            full_prompt,
            stream=True,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        print(f"Gemini API Error: {e}")
        yield f"\n\nError communicating with Gemini: {str(e)}"

def get_system_prompt():
    return """
    You are a helpful assistant that helps engineers, product managers and managers understand a codebase of multiple repositories.
    You will be given a list of repositiories with a description, as well as a list of contributors with their contributions.
    You will be asked to answer questions about the codebase, and you should find which contributor(s) are the most relevant to answer the question.
    Each contributor has a unique id that you will use to refer to them.
    Your answer should be markdown formatted, explain your reasoning and mention the contributor(s) you are referring to.
    When mentionning a contributor, use the format: <contributor id="id">contributor name</contributor>.
    For example: <contributor id="1">John Doe</contributor>. Do not start the tags with `.
    """


def get_user_prompt(user_question):
    """
    Formats repository and contributor data along with the user question
    into a structured prompt for the LLM.
    """
    data = DataSerializer()
    data = data.to_representation(data)
    repositories_data = data.get('repositories', [])
    contributors_data = data.get('contributors', [])

    # Create a lookup for repository names by ID for easy access later
    repo_id_to_name = {repo['id']: repo['name'] for repo in repositories_data}

    prompt_parts = []

    # --- Repositories Section ---
    prompt_parts.append("## Repositories\n")
    if repositories_data:
        for repo in repositories_data:
            prompt_parts.append(f"### Repository: {repo.get('name', 'N/A')} (ID: {repo.get('id', 'N/A')})")
            prompt_parts.append(f"**URL:** {repo.get('url', 'N/A')}")
            prompt_parts.append(f"**Summary:**\n{repo.get('summary', 'No summary provided.')}\n")
    else:
        prompt_parts.append("No repository data available.\n")

    prompt_parts.append("\n----------\n") # Separator

    # --- Contributors Section ---
    prompt_parts.append("## Contributors\n")
    if contributors_data:
        for contributor in contributors_data:
            prompt_parts.append(f"### Contributor: {contributor.get('username', 'N/A')} (ID: {contributor.get('id', 'N/A')})")
            prompt_parts.append(f"**URL:** {contributor.get('url', 'N/A')}")
            prompt_parts.append(f"**Overall Summary:**\n{contributor.get('summary', 'No summary provided.')}\n")

            works = contributor.get('works', [])
            if works:
                prompt_parts.append("**Contributions by Repository:**")
                for work in works:
                    repo_id = work.get('repository')
                    repo_name = repo_id_to_name.get(repo_id, f"Unknown Repo (ID: {repo_id})")
                    prompt_parts.append(f"- **Repository:** {repo_name}")
                    prompt_parts.append(f"  - **Work Summary:** {work.get('summary', 'No summary provided.')}")
                    # Optionally add Issue/Commit summaries if needed and available
                    issues = work.get('issues', [])
                    commits = work.get('commits', [])
                    if issues: 
                        prompt_parts.append("    - Relevant Issues:")
                        for issue in issues: # Limit for brevity
                            prompt_parts.append(f"      - {issue.get('summary', 'N/A')}")
                    if commits:
                        prompt_parts.append("    - Relevant Commits:")
                        for commit in commits: # Limit for brevity
                            prompt_parts.append(f"      - {commit.get('summary', 'N/A')}")
                prompt_parts.append("") # Add a newline after each contributor's works
            else:
                prompt_parts.append("No specific repository contributions listed.\n")
            prompt_parts.append("\n---\n") # Separator between contributors

    else:
        prompt_parts.append("No contributor data available.\n")

    prompt_parts.append("\n----------\n") # Separator

    # --- User Question Section ---
    prompt_parts.append("## User Question\n")
    prompt_parts.append(user_question)

    return "\n".join(prompt_parts)



@api_view(['POST'])
def llm_stream_view(request):
    """
    Handles POST requests containing a 'prompt' and returns a StreamingHttpResponse
    with the OpenAI completion stream.
    """
    user_question = request.data.get('prompt')

    if not user_question:
        return HttpResponseBadRequest("Missing 'prompt' in request body.")

    if not gemini_model:
         return JsonResponse({"error": "Gemini client not configured"}, status=503) # 503 Service Unavailable
    
    system_prompt = get_system_prompt()

    user_prompt = get_user_prompt(user_question)

    print(f"System Prompt: {system_prompt}")
    print(f"User Prompt: {user_prompt}")

    try:
        # Create the generator
        stream_generator = generate_gemini_stream(system_prompt, user_prompt)


        response = StreamingHttpResponse(
            stream_generator,
            content_type='text/plain; charset=utf-8' # Simpler for basic fetch handling
        )
        return response

    except Exception as e:
        # Catch potential errors during generator setup (though most are handled inside)
        print(f"Error setting up stream view: {e}")
        return JsonResponse({"error": f"Failed to start stream: {str(e)}"}, status=500)


# ============================================
# GAMIFICATION & LEADERBOARD ENDPOINTS
# ============================================

@api_view(['GET'])
def leaderboard(request):
    """Get top contributors leaderboard"""
    limit = int(request.GET.get('limit', 10))
    leaderboard_data = ContributorAnalytics.get_leaderboard(limit)
    return Response({'leaderboard': list(leaderboard_data)})


@api_view(['GET'])
def contributor_stats(request, contributor_id):
    """Get detailed stats for a contributor"""
    try:
        stats = ContributorAnalytics.get_contributor_stats(contributor_id)
        return Response(stats)
    except Contributor.DoesNotExist:
        return Response({'error': 'Contributor not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def award_badges(request, contributor_id):
    """Award badges to a contributor"""
    try:
        awarded = ContributorAnalytics.award_badges(contributor_id)
        return Response({
            'success': True,
            'badges_awarded': awarded,
            'count': len(awarded)
        })
    except Contributor.DoesNotExist:
        return Response({'error': 'Contributor not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def predict_burnout(request, contributor_id):
    """Predict burnout risk for a contributor"""
    try:
        prediction = ContributorAnalytics.predict_burnout(contributor_id)
        return Response(prediction)
    except Contributor.DoesNotExist:
        return Response({'error': 'Contributor not found'}, status=status.HTTP_404_NOT_FOUND)


# ============================================
# REPOSITORY ANALYTICS ENDPOINTS
# ============================================

@api_view(['GET'])
def repository_health(request, repo_id):
    """Get repository health metrics"""
    try:
        health_data = RepositoryAnalytics.get_repository_health(repo_id)
        return Response(health_data)
    except Repository.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def predict_completion(request, repo_id):
    """Predict project completion date"""
    try:
        prediction = RepositoryAnalytics.predict_completion(repo_id)
        return Response(prediction)
    except Repository.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)


# ============================================
# COLLABORATION NETWORK ENDPOINTS
# ============================================

@api_view(['GET'])
def collaboration_network(request):
    """Get collaboration network graph data"""
    repo_id = request.GET.get('repo_id', None)
    if repo_id:
        repo_id = int(repo_id)
    
    network_data = CollaborationAnalytics.get_collaboration_network(repo_id)
    return Response(network_data)


@api_view(['GET'])
def collaboration_patterns(request, repo_id):
    """Detect collaboration patterns in a repository"""
    try:
        patterns = CollaborationAnalytics.detect_collaboration_patterns(repo_id)
        return Response(patterns)
    except Repository.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)


# ============================================
# DASHBOARD ANALYTICS
# ============================================

@api_view(['GET'])
def dashboard_stats(request):
    """Get overall dashboard statistics"""
    total_contributors = Contributor.objects.count()
    total_repos = Repository.objects.count()
    total_commits = Commit.objects.count()
    total_issues = Issue.objects.count()
    
    # Active contributors (active in last 30 days)
    from django.utils import timezone
    from datetime import timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_contributors = Contributor.objects.filter(
        last_activity__gte=thirty_days_ago
    ).count()
    
    # Top repositories by health
    top_repos = Repository.objects.order_by('-health_score')[:5].values(
        'id', 'name', 'health_score', 'stars', 'avatar_url'
    )
    
    # Recent activity
    recent_activities = ActivityLog.objects.select_related(
        'contributor', 'repository'
    ).order_by('-timestamp')[:10].values(
        'contributor__username',
        'contributor__avatar_url',
        'repository__name',
        'activity_type',
        'timestamp'
    )
    
    return Response({
        'totals': {
            'contributors': total_contributors,
            'repositories': total_repos,
            'commits': total_commits,
            'issues': total_issues,
            'active_contributors': active_contributors,
        },
        'top_repositories': list(top_repos),
        'recent_activities': list(recent_activities),
    })


@api_view(['GET'])
def activity_trends(request):
    """Get activity trends over time"""
    days = int(request.GET.get('days', 30))
    from django.utils import timezone
    from datetime import timedelta
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Commits per day
    commits_per_day = Commit.objects.filter(
        committed_at__gte=start_date
    ).extra(
        select={'day': 'date(committed_at)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Issues per day
    issues_per_day = Issue.objects.filter(
        created_at__gte=start_date
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    return Response({
        'commits': list(commits_per_day),
        'issues': list(issues_per_day),
    })


# ============================================
# SEARCH & FILTER
# ============================================

@api_view(['GET'])
def search_contributors(request):
    """Search contributors by username, skills, or tags"""
    query = request.GET.get('q', '')
    skill = request.GET.get('skill', '')
    
    contributors = Contributor.objects.all()
    
    if query:
        contributors = contributors.filter(
            Q(username__icontains=query) |
            Q(bio__icontains=query) |
            Q(company__icontains=query)
        )
    
    if skill:
        contributors = contributors.filter(skill_tags__contains=skill)
    
    results = contributors.values(
        'id', 'username', 'avatar_url', 'total_score', 
        'level', 'skill_tags', 'preferred_work_hours'
    )[:20]
    
    return Response({'results': list(results)})


# ============================================
# GITHUB IMPORT
# ============================================

@api_view(['POST'])
def import_github_repository(request):
    """
    Import a GitHub repository and all its data
    POST /api/repositories/import/
    Body: {"repo_url": "https://github.com/owner/repo"}
    """
    from .github_importer import GitHubImporter
    
    repo_url = request.data.get('repo_url')
    github_token = request.data.get('github_token')  # Optional
    
    if not repo_url:
        return Response({
            'error': 'repo_url is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Initialize importer
        importer = GitHubImporter(github_token)
        
        # Import repository
        print(f"Starting import for: {repo_url}")
        repository = importer.import_repository(repo_url)
        
        return Response({
            'success': True,
            'message': f'Successfully imported {repository.name}',
            'repository': {
                'id': repository.id,
                'name': repository.name,
                'url': repository.url,
                'stars': repository.stars,
                'forks': repository.forks,
                'contributors_count': repository.works.values('contributor').distinct().count(),
                'commits_count': Commit.objects.filter(repository=repository).count(),
                'issues_count': Issue.objects.filter(work__repository=repository).count(),
            }
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        print(f"Error importing repository: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'error': f'Failed to import repository: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def import_status(request):
    """
    Get status of repositories that have been imported
    GET /api/repositories/import-status/
    """
    repositories = Repository.objects.all().values(
        'id', 'name', 'url', 'stars', 'forks', 
        'created_at', 'updated_at'
    ).annotate(
        contributors_count=Count('works__contributor', distinct=True),
        commits_count=Count('commits', distinct=True),
    )
    
    return Response({
        'repositories': list(repositories),
        'total': repositories.count()
    })


@api_view(['POST'])
def sync_repository(request, repo_id):
    """
    Sync a specific repository with latest GitHub data
    POST /api/repositories/<repo_id>/sync/
    """
    from .github_importer import GitHubImporter
    
    github_token = request.data.get('github_token')
    
    try:
        repository = Repository.objects.get(id=repo_id)
    except Repository.DoesNotExist:
        return Response({
            'error': 'Repository not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Re-import to sync latest data
        importer = GitHubImporter(github_token)
        print(f"Syncing repository: {repository.url}")
        updated_repo = importer.import_repository(repository.url)
        
        return Response({
            'success': True,
            'message': f'Successfully synced {repository.name}',
            'repository': {
                'id': updated_repo.id,
                'name': updated_repo.name,
                'url': updated_repo.url,
                'stars': updated_repo.stars,
                'forks': updated_repo.forks,
                'contributors_count': updated_repo.works.values('contributor').distinct().count(),
                'commits_count': Commit.objects.filter(repository=updated_repo).count(),
                'issues_count': Issue.objects.filter(work__repository=updated_repo).count(),
                'updated_at': updated_repo.updated_at,
            }
        })
    
    except Exception as e:
        print(f"Error syncing repository: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'error': f'Failed to sync repository: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# COMMIT ANALYTICS
# ============================================

@api_view(['GET'])
def commit_analytics(request):
    """
    Get all commits with contributor info and AI-generated summaries
    GET /api/commits/analytics/
    Query params:
    - repo_id: Filter by repository ID
    - contributor_id: Filter by contributor ID
    - limit: Number of commits to return (default: 50)
    """
    from django.utils import timezone
    from datetime import datetime
    
    # Get query parameters
    repo_id = request.GET.get('repo_id')
    contributor_id = request.GET.get('contributor_id')
    limit = int(request.GET.get('limit', 50))
    
    # Build query
    commits = Commit.objects.select_related('contributor', 'repository').all()
    
    if repo_id:
        commits = commits.filter(repository_id=repo_id)
    
    if contributor_id:
        commits = commits.filter(contributor_id=contributor_id)
    
    # Order by most recent first
    commits = commits.order_by('-committed_at')[:limit]
    
    # Format commit data
    commit_data = []
    for commit in commits:
        # Generate AI summary if not already generated
        summary = commit.summary
        if len(summary) > 100 and not summary.startswith('AI:'):
            # Truncate long summaries and generate AI summary
            summary = generate_commit_summary(commit.summary, commit.additions, commit.deletions)
        
        commit_data.append({
            'id': commit.id,
            'url': commit.url,
            'summary': summary,
            'committed_at': commit.committed_at,
            'additions': commit.additions,
            'deletions': commit.deletions,
            'files_changed': commit.files_changed,
            'churn': commit.code_churn_ratio,
            'contributor': {
                'id': commit.contributor.id if commit.contributor else None,
                'username': commit.contributor.username if commit.contributor else 'Unknown',
                'avatar_url': commit.contributor.avatar_url if commit.contributor else '',
                'url': commit.contributor.url if commit.contributor else '',
            },
            'repository': {
                'id': commit.repository.id if commit.repository else None,
                'name': commit.repository.name if commit.repository else 'Unknown',
                'url': commit.repository.url if commit.repository else '',
            }
        })
    
    return Response({
        'commits': commit_data,
        'total': len(commit_data),
        'filters': {
            'repo_id': repo_id,
            'contributor_id': contributor_id,
            'limit': limit
        }
    })


def generate_commit_summary(commit_message, additions, deletions):
    """
    Generate AI summary for commit using Gemini API with retry logic
    """
    if not gemini_model:
        return commit_message[:200]  # Return truncated if no API client
    
    max_retries = 3
    base_delay = 5  # Start with 5 seconds
    
    for attempt in range(max_retries):
        try:
            # Add rate limiting delay between calls (avoid hitting 15 RPM limit)
            if attempt > 0:
                wait_time = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"Rate limit retry {attempt + 1}/{max_retries}, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                time.sleep(0.5)  # Small delay to avoid rapid consecutive calls
            
            prompt = f"""Summarize this git commit in one concise sentence (max 15 words):

Commit message: {commit_message[:500]}
Changes: +{additions} lines, -{deletions} lines

Summary:"""
            
            response = gemini_model.generate_content(prompt)
            ai_summary = response.text.strip()
            return f"AI: {ai_summary}"
        
        except Exception as e:
            error_str = str(e)
            if '429' in error_str or 'quota' in error_str.lower():
                print(f"Rate limit hit (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    print("Max retries reached, returning fallback")
                    return commit_message[:200]
            else:
                print(f"Error generating commit summary: {e}")
                return commit_message[:200]
    
    return commit_message[:200]


@api_view(['GET'])
def contributor_commit_summaries(request):
    """
    Get commits grouped by contributor with AI-generated summaries of their work
    GET /api/commits/contributor-summaries/
    Query params:
    - repo_id: Filter by repository ID
    """
    from django.db.models import Count, Sum
    
    repo_id = request.GET.get('repo_id')
    
    # Get all contributors with commits
    contributors_query = Contributor.objects.annotate(
        commit_count=Count('commits')
    ).filter(commit_count__gt=0)
    
    if repo_id:
        contributors_query = contributors_query.filter(commits__repository_id=repo_id).distinct()
    
    contributors_query = contributors_query.order_by('-commit_count')
    
    summaries_data = []
    
    for contributor in contributors_query:
        # Get contributor's commits
        commits_query = contributor.commits.select_related('repository').all()
        
        if repo_id:
            commits_query = commits_query.filter(repository_id=repo_id)
        
        commits_query = commits_query.order_by('-committed_at')
        
        # Calculate contributor stats
        total_additions = commits_query.aggregate(Sum('additions'))['additions__sum'] or 0
        total_deletions = commits_query.aggregate(Sum('deletions'))['deletions__sum'] or 0
        total_files = commits_query.aggregate(Sum('files_changed'))['files_changed__sum'] or 0
        
        # Get all commit messages for AI summary
        commit_messages = [commit.summary for commit in commits_query[:20]]  # Limit to 20 for API
        
        # Generate overall work summary
        work_summary = generate_contributor_work_summary(
            contributor.username,
            commit_messages,
            total_additions,
            total_deletions,
            commits_query.count()
        )
        
        # Format individual commits
        commits_list = []
        for commit in commits_query[:10]:  # Show top 10 commits
            commit_summary = commit.summary
            if len(commit_summary) > 100 and not commit_summary.startswith('AI:'):
                commit_summary = generate_commit_summary(
                    commit.summary, 
                    commit.additions, 
                    commit.deletions
                )
            
            commits_list.append({
                'id': commit.id,
                'url': commit.url,
                'summary': commit_summary,
                'committed_at': commit.committed_at,
                'additions': commit.additions,
                'deletions': commit.deletions,
                'files_changed': commit.files_changed,
                'repository': {
                    'id': commit.repository.id if commit.repository else None,
                    'name': commit.repository.name if commit.repository else 'Unknown',
                    'url': commit.repository.url if commit.repository else '',
                }
            })
        
        summaries_data.append({
            'contributor': {
                'id': contributor.id,
                'username': contributor.username,
                'avatar_url': contributor.avatar_url,
                'url': contributor.url,
            },
            'stats': {
                'total_commits': commits_query.count(),
                'total_additions': total_additions,
                'total_deletions': total_deletions,
                'total_files_changed': total_files,
                'lines_changed': total_additions + total_deletions,
            },
            'work_summary': work_summary,
            'recent_commits': commits_list,
        })
    
    return Response({
        'success': True,
        'contributors': summaries_data,
        'total_contributors': len(summaries_data),
        'repository_id': repo_id,
    })


def generate_contributor_work_summary(username, commit_messages, additions, deletions, commit_count):
    """
    Generate AI summary of what a contributor has worked on using Gemini API with retry logic
    """
    if not gemini_model or not commit_messages:
        return f"{username} made {commit_count} commits with {additions} additions and {deletions} deletions."
    
    max_retries = 3
    base_delay = 5  # Start with 5 seconds
    
    for attempt in range(max_retries):
        try:
            # Add rate limiting delay between calls
            if attempt > 0:
                wait_time = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"Rate limit retry {attempt + 1}/{max_retries}, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                time.sleep(0.5)  # Small delay to avoid rapid consecutive calls
            
            # Combine commit messages
            messages_text = "\n- ".join(commit_messages[:10])  # Limit to 10 messages
            
            prompt = f"""Analyze these git commits by {username} and provide a 2-3 sentence summary of their work. Focus on:
1. What features or components they worked on
2. What problems they solved
3. Their main contributions

Commits:
- {messages_text}

Stats: {commit_count} commits, +{additions} lines, -{deletions} lines

Provide a professional summary:"""
            
            response = gemini_model.generate_content(prompt)
            ai_summary = response.text.strip()
            return ai_summary
        
        except Exception as e:
            error_str = str(e)
            if '429' in error_str or 'quota' in error_str.lower():
                print(f"Rate limit hit (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    print("Max retries reached, returning fallback")
                    return f"{username} made {commit_count} commits focusing on various features and improvements. Total changes: +{additions}/-{deletions} lines across the project."
            else:
                print(f"Error generating contributor work summary: {e}")
                return f"{username} made {commit_count} commits focusing on various features and improvements. Total changes: +{additions}/-{deletions} lines across the project."
    
    return f"{username} made {commit_count} commits focusing on various features and improvements. Total changes: +{additions}/-{deletions} lines across the project."


@api_view(['GET'])
def commit_timeline(request):
    """
    Get commit timeline grouped by date
    GET /api/commits/timeline/
    """
    from django.db.models.functions import TruncDate
    from collections import defaultdict
    
    repo_id = request.GET.get('repo_id')
    days = int(request.GET.get('days', 30))
    
    commits = Commit.objects.select_related('contributor', 'repository')
    
    if repo_id:
        commits = commits.filter(repository_id=repo_id)
    
    # Get commits from last N days
    from datetime import timedelta
    from django.utils import timezone
    start_date = timezone.now() - timedelta(days=days)
    commits = commits.filter(committed_at__gte=start_date)
    
    # Group by date
    timeline = defaultdict(list)
    for commit in commits.order_by('-committed_at'):
        date_key = commit.committed_at.strftime('%Y-%m-%d')
        timeline[date_key].append({
            'id': commit.id,
            'summary': commit.summary[:100],
            'contributor': commit.contributor.username if commit.contributor else 'Unknown',
            'avatar_url': commit.contributor.avatar_url if commit.contributor else '',
            'time': commit.committed_at.strftime('%H:%M'),
            'additions': commit.additions,
            'deletions': commit.deletions,
        })
    
    return Response({
        'timeline': dict(timeline),
        'total_commits': sum(len(commits) for commits in timeline.values()),
        'days': days
    })
