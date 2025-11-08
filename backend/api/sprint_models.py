"""
Sprint Planning Models
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .models import Repository, Contributor, Issue, Organization, Team


class Sprint(models.Model):
    """Sprint model for agile planning"""
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Relationships
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='sprints')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, 
                                     related_name='sprints', null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, 
                            related_name='sprints', null=True, blank=True)
    
    # Sprint timeline
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Sprint metrics
    planned_velocity = models.IntegerField(default=0)  # Story points planned
    actual_velocity = models.IntegerField(default=0)   # Story points completed
    total_issues = models.IntegerField(default=0)
    completed_issues = models.IntegerField(default=0)
    
    # Capacity planning
    team_capacity = models.IntegerField(default=0)  # Available person-hours
    allocated_hours = models.IntegerField(default=0)  # Hours allocated to tasks
    
    # AI-generated insights
    ai_suggested = models.BooleanField(default=False)
    suggestion_metadata = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, 
                                    null=True, related_name='created_sprints')
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['repository', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.repository.name})"
    
    @property
    def duration_days(self):
        """Calculate sprint duration in days"""
        return (self.end_date - self.start_date).days
    
    @property
    def completion_rate(self):
        """Calculate sprint completion rate"""
        if self.total_issues == 0:
            return 0.0
        return (self.completed_issues / self.total_issues) * 100
    
    @property
    def velocity_accuracy(self):
        """Calculate how accurate the velocity estimate was"""
        if self.planned_velocity == 0:
            return 0.0
        return (self.actual_velocity / self.planned_velocity) * 100
    
    def calculate_progress(self):
        """Calculate current sprint progress"""
        issues = self.sprint_issues.all()
        self.total_issues = issues.count()
        self.completed_issues = issues.filter(status='completed').count()
        self.actual_velocity = issues.filter(status='completed').aggregate(
            total=models.Sum('story_points')
        )['total'] or 0
        self.save()
        return {
            'total': self.total_issues,
            'completed': self.completed_issues,
            'in_progress': issues.filter(status='in_progress').count(),
            'todo': issues.filter(status='todo').count(),
            'completion_rate': self.completion_rate,
        }


class SprintIssue(models.Model):
    """Issues assigned to a sprint"""
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.AutoField(primary_key=True)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name='sprint_issues')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, 
                             related_name='sprint_assignments', null=True, blank=True)
    
    # Issue details (if not linked to existing Issue)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    issue_type = models.CharField(max_length=50, default='task')  # task, bug, feature, story
    
    # Assignment
    assigned_to = models.ForeignKey(Contributor, on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='assigned_issues')
    
    # Estimation
    story_points = models.IntegerField(default=0)
    estimated_hours = models.FloatField(default=0.0)
    actual_hours = models.FloatField(default=0.0, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # AI suggestions
    ai_assigned = models.BooleanField(default=False)
    ai_reasoning = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'created_at']
        indexes = [
            models.Index(fields=['sprint', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.sprint.name})"


class TeamMemberCapacity(models.Model):
    """Track team member capacity for sprint planning"""
    id = models.AutoField(primary_key=True)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name='team_capacities')
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE, 
                                   related_name='sprint_capacities')
    
    # Capacity in hours
    total_capacity_hours = models.FloatField(default=40.0)  # Default: 1 week = 40 hours
    allocated_hours = models.FloatField(default=0.0)
    
    # Availability factors
    availability_percentage = models.FloatField(default=100.0)  # 0-100
    time_off_hours = models.FloatField(default=0.0)
    other_commitments_hours = models.FloatField(default=0.0)
    
    # Historical velocity
    average_velocity = models.FloatField(default=0.0)  # Story points per sprint
    average_hours_per_point = models.FloatField(default=4.0)  # Hours per story point
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['sprint', 'contributor']
        ordering = ['contributor__username']
    
    def __str__(self):
        return f"{self.contributor.username} - {self.sprint.name}"
    
    @property
    def available_hours(self):
        """Calculate actual available hours"""
        base_capacity = self.total_capacity_hours * (self.availability_percentage / 100)
        return base_capacity - self.time_off_hours - self.other_commitments_hours
    
    @property
    def remaining_hours(self):
        """Calculate remaining capacity"""
        return self.available_hours - self.allocated_hours
    
    @property
    def utilization_percentage(self):
        """Calculate current utilization"""
        if self.available_hours == 0:
            return 0.0
        return (self.allocated_hours / self.available_hours) * 100


class SprintVelocityHistory(models.Model):
    """Historical sprint velocity for prediction"""
    id = models.AutoField(primary_key=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, 
                                  related_name='velocity_history')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, 
                            null=True, blank=True, related_name='velocity_history')
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, 
                              related_name='velocity_records')
    
    # Velocity metrics
    planned_velocity = models.IntegerField(default=0)
    actual_velocity = models.IntegerField(default=0)
    team_size = models.IntegerField(default=0)
    
    # Completion metrics
    total_issues = models.IntegerField(default=0)
    completed_issues = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    
    # Time tracking
    planned_hours = models.FloatField(default=0.0)
    actual_hours = models.FloatField(default=0.0)
    
    sprint_start = models.DateField()
    sprint_end = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sprint_start']
        indexes = [
            models.Index(fields=['repository', '-sprint_start']),
            models.Index(fields=['team', '-sprint_start']),
        ]
    
    def __str__(self):
        return f"{self.repository.name} - {self.sprint.name} (Velocity: {self.actual_velocity})"
