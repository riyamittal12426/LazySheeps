"""
Role-Based Access Control (RBAC) Models
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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
        from api.models import Repository
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
    repository = models.ForeignKey('api.Repository', on_delete=models.CASCADE, related_name='access_controls')
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
