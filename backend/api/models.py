from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import json

# Create your models here.


class User(AbstractUser):
    """Custom user model with profile information"""
    bio = models.TextField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    github_username = models.CharField(max_length=255, blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    
    # Profile stats
    total_repositories = models.IntegerField(default=0)
    total_commits = models.IntegerField(default=0)
    total_contributions = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


# ============================================================================
# RBAC & Multi-Tenant Models
# ============================================================================

class Organization(models.Model):
    """
    Multi-tenant organization model
    Each organization can have multiple teams, repositories, and members
    """
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('business', 'Business'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    
    # Branding (White-label)
    primary_color = models.CharField(max_length=7, default='#7c3aed')  # Purple
    secondary_color = models.CharField(max_length=7, default='#3b82f6')  # Blue
    custom_domain = models.CharField(max_length=255, blank=True, null=True)
    
    # Subscription
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    max_repositories = models.IntegerField(default=3)  # Free tier limit
    max_members = models.IntegerField(default=5)
    
    # Owner
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return self.name
    
    def can_add_repository(self):
        """Check if organization can add more repositories"""
        current_count = Repository.objects.filter(organization=self).count()
        return current_count < self.max_repositories
    
    def can_add_member(self):
        """Check if organization can add more members"""
        current_count = self.members.count()
        return current_count < self.max_members


class OrganizationMember(models.Model):
    """
    Organization membership with roles
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('developer', 'Developer'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='developer')
    
    # Permissions
    can_manage_members = models.BooleanField(default=False)
    can_manage_repositories = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=True)
    can_export_data = models.BooleanField(default=False)
    
    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invited_members')
    
    class Meta:
        unique_together = ['organization', 'user']
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['organization', 'user']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"
    
    def save(self, *args, **kwargs):
        """Auto-set permissions based on role"""
        if self.role in ['owner', 'admin']:
            self.can_manage_members = True
            self.can_manage_repositories = True
            self.can_view_analytics = True
            self.can_export_data = True
        elif self.role == 'manager':
            self.can_manage_members = False
            self.can_manage_repositories = True
            self.can_view_analytics = True
            self.can_export_data = True
        elif self.role == 'developer':
            self.can_manage_members = False
            self.can_manage_repositories = False
            self.can_view_analytics = True
            self.can_export_data = False
        elif self.role == 'viewer':
            self.can_manage_members = False
            self.can_manage_repositories = False
            self.can_view_analytics = True
            self.can_export_data = False
        
        super().save(*args, **kwargs)


class Team(models.Model):
    """
    Teams within an organization
    """
    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Members
    members = models.ManyToManyField(User, through='TeamMember', related_name='teams')
    
    # Team lead
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_teams')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['organization', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class TeamMember(models.Model):
    """
    Team membership
    """
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['team', 'user']
    
    def __str__(self):
        return f"{self.user.username} in {self.team.name}"


class AuditLog(models.Model):
    """
    Audit log for tracking all actions
    """
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('invite', 'Invite'),
        ('remove', 'Remove'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=50)  # 'repository', 'member', 'team', etc.
    resource_id = models.IntegerField(null=True, blank=True)
    resource_name = models.CharField(max_length=255, blank=True)
    
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['organization', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action} {self.resource_type} at {self.timestamp}"


# ============================================================================
# Core Application Models
# ============================================================================

class Repository(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null=True)  # owner/repo
    avatar_url = models.URLField()
    url = models.URLField()
    summary = models.TextField()
    raw_data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Organization (RBAC)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, 
                                     related_name='repositories', null=True, blank=True)
    is_private = models.BooleanField(default=False)
    
    # Health & Analytics
    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)
    open_issues = models.IntegerField(default=0)
    health_score = models.FloatField(default=0.0)
    activity_trend = models.CharField(max_length=20, default='stable')  # up, down, stable
    primary_language = models.CharField(max_length=100, blank=True, null=True)
    
    # Predictive Analytics
    predicted_completion_date = models.DateField(blank=True, null=True)
    velocity_score = models.FloatField(default=0.0)
    
    # DORA Metrics
    deployment_frequency = models.FloatField(default=0.0)  # deploys per day
    lead_time_for_changes = models.FloatField(default=0.0)  # hours
    mean_time_to_recovery = models.FloatField(default=0.0)  # hours
    change_failure_rate = models.FloatField(default=0.0)  # percentage
    
    class Meta:
        verbose_name_plural = "Repositories"
        ordering = ['-stars']

    def __str__(self):
        return self.name
    
    def calculate_health_score(self):
        """Calculate repository health based on activity and metrics"""
        score = 0
        # Active commits in last 30 days
        recent_commits = self.commits.filter(
            committed_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        score += min(recent_commits * 2, 40)  # Max 40 points
        
        # Issue resolution rate
        if self.open_issues > 0:
            # Get issues through RepositoryWork relationship
            closed_issues = Issue.objects.filter(
                work__repository=self,
                state='closed'
            ).count()
            total_issues = Issue.objects.filter(work__repository=self).count()
            if total_issues > 0:
                resolution_rate = closed_issues / total_issues
                score += resolution_rate * 30  # Max 30 points
        
        # Contributor diversity (more contributors = healthier)
        contributor_count = self.works.values('contributor').distinct().count()
        score += min(contributor_count * 3, 30)  # Max 30 points
        
        self.health_score = min(score, 100)
        self.save()
        return self.health_score

    
class Contributor(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    url = models.URLField()
    avatar_url = models.URLField()
    summary = models.TextField()    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Gamification Fields
    total_commits = models.IntegerField(default=0)
    total_issues_closed = models.IntegerField(default=0)
    total_prs_reviewed = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    experience_points = models.IntegerField(default=0)
    
    # Activity Pattern Analysis
    preferred_work_hours = models.CharField(max_length=50, blank=True, null=True)  # morning, afternoon, evening, night
    activity_streak = models.IntegerField(default=0)  # consecutive days
    last_activity = models.DateTimeField(blank=True, null=True)
    
    # AI-Generated Insights
    coding_pattern = models.JSONField(default=dict, blank=True)  # Stores AI analysis
    skill_tags = models.JSONField(default=list, blank=True)  # e.g., ["backend", "python", "API"]
    burnout_risk_score = models.FloatField(default=0.0)  # 0-1 scale
    collaboration_score = models.FloatField(default=0.0)  # How well they work with others
    
    # Location & Bio
    location = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-total_score', '-level']

    def __str__(self):
        return self.username
    
    def calculate_score(self):
        """Calculate gamification score and level"""
        # Score calculation
        score = (
            self.total_commits * 10 +
            self.total_issues_closed * 25 +
            self.total_prs_reviewed * 15
        )
        
        # Bonus for streak
        if self.activity_streak > 7:
            score += self.activity_streak * 5
        
        self.total_score = score
        self.experience_points = score
        
        # Level calculation (every 1000 XP = 1 level)
        self.level = max(1, self.experience_points // 1000)
        
        self.save()
        return self.total_score
    
    def update_activity_streak(self):
        """Update consecutive activity days"""
        if self.last_activity:
            days_diff = (timezone.now().date() - self.last_activity.date()).days
            if days_diff == 1:
                self.activity_streak += 1
            elif days_diff > 1:
                self.activity_streak = 1
        else:
            self.activity_streak = 1
        
        self.last_activity = timezone.now()
        self.save()
    
    def analyze_work_pattern(self):
        """Analyze when contributor is most active"""
        commits = self.commits.all()
        if not commits.exists():
            return None
        
        hour_counts = {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0}
        
        for commit in commits:
            hour = commit.committed_at.hour
            if 5 <= hour < 12:
                hour_counts['morning'] += 1
            elif 12 <= hour < 17:
                hour_counts['afternoon'] += 1
            elif 17 <= hour < 22:
                hour_counts['evening'] += 1
            else:
                hour_counts['night'] += 1
        
        self.preferred_work_hours = max(hour_counts, key=hour_counts.get)
        self.save()
        return self.preferred_work_hours


class RepositoryAccess(models.Model):
    """
    Repository access control
    """
    ACCESS_LEVELS = [
        ('none', 'No Access'),
        ('read', 'Read'),
        ('write', 'Write'),
        ('admin', 'Admin'),
    ]
    
    id = models.AutoField(primary_key=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='access_controls')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repository_access')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='repository_access')
    
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVELS, default='read')
    
    # Metadata
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_access')
    
    class Meta:
        unique_together = [['repository', 'user'], ['repository', 'team']]
        ordering = ['-granted_at']
    
    def __str__(self):
        target = self.user.username if self.user else self.team.name
        return f"{target} - {self.repository.name} ({self.access_level})"


class RepositoryWork(models.Model):
    id = models.AutoField(primary_key=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='works')
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name='works')
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Contribution metrics
    commit_count = models.IntegerField(default=0)
    issue_count = models.IntegerField(default=0)
    lines_added = models.IntegerField(default=0)
    lines_removed = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['repository', 'contributor']

    def __str__(self):
        return f"{self.contributor.username} - {self.repository.name}"
    
class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    work = models.ForeignKey(RepositoryWork, on_delete=models.CASCADE, related_name='issues')
    url = models.URLField()
    raw_data = models.JSONField()
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for analytics
    state = models.CharField(max_length=20, default='open')  # open, closed
    is_bug = models.BooleanField(default=False)
    is_feature = models.BooleanField(default=False)
    priority = models.CharField(max_length=20, default='medium')  # low, medium, high, critical
    
    def __str__(self):
        return f"Issue #{self.id} - {self.work.repository.name}"

class Commit(models.Model):
    id = models.AutoField(primary_key=True)
    work = models.ForeignKey(RepositoryWork, on_delete=models.CASCADE, related_name='commits')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='commits', null=True)
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name='commits', null=True)
    url = models.URLField()
    raw_data = models.JSONField()
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Code quality metrics
    additions = models.IntegerField(default=0)
    deletions = models.IntegerField(default=0)
    files_changed = models.IntegerField(default=0)
    committed_at = models.DateTimeField(blank=True, null=True)
    code_churn_ratio = models.FloatField(default=0.0)  # deletions / (additions + deletions)
    
    def __str__(self):
        return f"Commit #{self.id} - {self.work.repository.name}"
    
    def calculate_churn(self):
        """Calculate code churn ratio"""
        total = self.additions + self.deletions
        if total > 0:
            self.code_churn_ratio = self.deletions / total
        else:
            self.code_churn_ratio = 0.0
        self.save()


class Badge(models.Model):
    """Gamification badges"""
    BADGE_TYPES = [
        ('early_bird', '🌅 Early Bird'),
        ('night_owl', '🦉 Night Owl'),
        ('bug_hunter', '🐛 Bug Hunter'),
        ('feature_master', '⭐ Feature Master'),
        ('code_reviewer', '👀 Code Reviewer'),
        ('streak_master', '🔥 Streak Master'),
        ('team_player', '🤝 Team Player'),
        ('innovator', '💡 Innovator'),
        ('consistent', '📊 Consistent Contributor'),
        ('speedster', '⚡ Speedster'),
    ]
    
    id = models.AutoField(primary_key=True)
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name='badges')
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPES)
    earned_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['contributor', 'badge_type']
        ordering = ['-earned_date']
    
    def __str__(self):
        return f"{self.contributor.username} - {self.get_badge_type_display()}"


class Collaboration(models.Model):
    """Track collaborations between contributors"""
    id = models.AutoField(primary_key=True)
    contributor_1 = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name='collaborations_from')
    contributor_2 = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name='collaborations_to')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='collaborations')
    
    # Collaboration metrics
    shared_commits = models.IntegerField(default=0)
    code_reviews = models.IntegerField(default=0)
    issue_discussions = models.IntegerField(default=0)
    collaboration_strength = models.FloatField(default=0.0)  # 0-1 scale
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['contributor_1', 'contributor_2', 'repository']
    
    def __str__(self):
        return f"{self.contributor_1.username} <-> {self.contributor_2.username}"
    
    def calculate_strength(self):
        """Calculate collaboration strength"""
        total_interactions = self.shared_commits + self.code_reviews * 2 + self.issue_discussions
        # Normalize to 0-1 scale (100+ interactions = 1.0)
        self.collaboration_strength = min(total_interactions / 100.0, 1.0)
        self.save()
        return self.collaboration_strength


class ActivityLog(models.Model):
    """Track all contributor activities for analytics"""
    ACTIVITY_TYPES = [
        ('commit', 'Commit'),
        ('issue_created', 'Issue Created'),
        ('issue_closed', 'Issue Closed'),
        ('pr_opened', 'PR Opened'),
        ('pr_reviewed', 'PR Reviewed'),
        ('comment', 'Comment'),
    ]
    
    id = models.AutoField(primary_key=True)
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name='activities')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['contributor', '-timestamp']),
            models.Index(fields=['repository', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.contributor.username} - {self.activity_type} at {self.timestamp}"
