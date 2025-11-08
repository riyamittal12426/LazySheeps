"""
RBAC ViewSets for Organizations, Teams, and Access Control
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from api.models import (
    Organization, OrganizationMember, Team, TeamMember,
    RepositoryAccess, AuditLog, User, Repository
)
from api.rbac_serializers import (
    OrganizationSerializer, OrganizationMemberSerializer,
    TeamSerializer, TeamMemberSerializer,
    RepositoryAccessSerializer, AuditLogSerializer,
    OrganizationInviteSerializer
)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Organization CRUD operations
    """
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return organizations where user is a member"""
        return Organization.objects.filter(
            Q(owner=self.request.user) |
            Q(members__user=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        """Create organization and add creator as owner"""
        org = serializer.save(owner=self.request.user)
        
        # Add creator as owner member
        OrganizationMember.objects.create(
            organization=org,
            user=self.request.user,
            role='owner'
        )
        
        # Log action
        AuditLog.objects.create(
            organization=org,
            user=self.request.user,
            action='create',
            resource_type='organization',
            resource_id=org.id,
            resource_name=org.name,
            details={'plan': org.plan}
        )
    
    @action(detail=True, methods=['post'])
    def invite_member(self, request, pk=None):
        """Invite a member to the organization"""
        org = self.get_object()
        serializer = OrganizationInviteSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user can manage members
        membership = OrganizationMember.objects.filter(
            organization=org,
            user=request.user
        ).first()
        
        if not membership or not membership.can_manage_members:
            return Response(
                {'error': 'You do not have permission to invite members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if organization can add more members
        if not org.can_add_member():
            return Response(
                {'error': f'Organization has reached maximum members ({org.max_members})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user by email
        user = User.objects.get(email=serializer.validated_data['email'])
        
        # Check if already a member
        if OrganizationMember.objects.filter(organization=org, user=user).exists():
            return Response(
                {'error': 'User is already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create membership
        member = OrganizationMember.objects.create(
            organization=org,
            user=user,
            role=serializer.validated_data['role'],
            invited_by=request.user
        )
        
        # Log action
        AuditLog.objects.create(
            organization=org,
            user=request.user,
            action='invite',
            resource_type='member',
            resource_id=member.id,
            resource_name=user.username,
            details={'role': member.role}
        )
        
        return Response(
            OrganizationMemberSerializer(member).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """List all members of the organization"""
        org = self.get_object()
        members = OrganizationMember.objects.filter(organization=org)
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """Remove a member from the organization"""
        org = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        membership = OrganizationMember.objects.filter(
            organization=org,
            user=request.user
        ).first()
        
        if not membership or not membership.can_manage_members:
            return Response(
                {'error': 'You do not have permission to remove members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Cannot remove owner
        member_to_remove = get_object_or_404(
            OrganizationMember,
            organization=org,
            user_id=user_id
        )
        
        if member_to_remove.role == 'owner':
            return Response(
                {'error': 'Cannot remove organization owner'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log action before deletion
        AuditLog.objects.create(
            organization=org,
            user=request.user,
            action='remove',
            resource_type='member',
            resource_id=member_to_remove.id,
            resource_name=member_to_remove.user.username,
            details={'role': member_to_remove.role}
        )
        
        member_to_remove.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['delete'])
    def remove_repository(self, request, pk=None):
        """Remove a repository from the organization"""
        org = self.get_object()
        repository_id = request.data.get('repository_id')
        
        if not repository_id:
            return Response(
                {'error': 'repository_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions - must be owner or admin
        membership = OrganizationMember.objects.filter(
            organization=org,
            user=request.user
        ).first()
        
        if not membership or membership.role not in ['owner', 'admin']:
            return Response(
                {'error': 'You do not have permission to remove repositories'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get repository
        repository = get_object_or_404(
            Repository,
            id=repository_id,
            organization=org
        )
        
        # Log action before deletion
        AuditLog.objects.create(
            organization=org,
            user=request.user,
            action='remove',
            resource_type='repository',
            resource_id=repository.id,
            resource_name=repository.name,
            details={
                'full_name': repository.full_name,
                'stars': repository.stars
            }
        )
        
        # Remove organization association (or delete entirely based on your needs)
        # Option 1: Just remove from organization (keep repository data)
        repository.organization = None
        repository.save()
        
        # Option 2: Delete entirely (uncomment if you want this behavior)
        # repository.delete()
        
        return Response(
            {'message': f'Repository {repository.name} removed from organization'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def repositories(self, request, pk=None):
        """List all repositories in the organization"""
        org = self.get_object()
        repositories = Repository.objects.filter(organization=org)
        
        # Simple serialization (you can create a dedicated serializer if needed)
        data = [{
            'id': repo.id,
            'name': repo.name,
            'full_name': repo.full_name,
            'url': repo.url,
            'stars': repo.stars,
            'forks': repo.forks,
            'is_private': repo.is_private,
            'health_score': repo.health_score
        } for repo in repositories]
        
        return Response(data)


class TeamViewSet(viewsets.ModelViewSet):
    """
    Team CRUD operations
    """
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return teams in user's organizations"""
        user_orgs = Organization.objects.filter(
            Q(owner=self.request.user) |
            Q(members__user=self.request.user)
        )
        return Team.objects.filter(organization__in=user_orgs)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, id=user_id)
        
        # Check if user is member of organization
        if not OrganizationMember.objects.filter(
            organization=team.organization,
            user=user
        ).exists():
            return Response(
                {'error': 'User is not a member of the organization'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already a team member
        if TeamMember.objects.filter(team=team, user=user).exists():
            return Response(
                {'error': 'User is already a team member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add to team
        team_member = TeamMember.objects.create(team=team, user=user)
        
        return Response(
            TeamMemberSerializer(team_member).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """List all members of the team"""
        team = self.get_object()
        members = TeamMember.objects.filter(team=team)
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Audit log viewing (read-only)
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return audit logs for user's organizations"""
        user_orgs = Organization.objects.filter(
            Q(owner=self.request.user) |
            Q(members__user=self.request.user)
        )
        return AuditLog.objects.filter(organization__in=user_orgs)
