"""
RBAC Serializers for Organizations, Teams, and Access Control
"""
from rest_framework import serializers
from api.models import (
    Organization, OrganizationMember, Team, TeamMember,
    RepositoryAccess, AuditLog, User
)


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested serialization"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer with member count"""
    owner = UserBasicSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    repository_count = serializers.SerializerMethodField()
    can_add_repo = serializers.SerializerMethodField()
    can_add_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description', 'logo_url',
            'primary_color', 'secondary_color', 'custom_domain',
            'plan', 'max_repositories', 'max_members',
            'owner', 'created_at', 'updated_at', 'is_active',
            'member_count', 'repository_count',
            'can_add_repo', 'can_add_member'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_repository_count(self, obj):
        return obj.repositories.count()
    
    def get_can_add_repo(self, obj):
        return obj.can_add_repository()
    
    def get_can_add_member(self, obj):
        return obj.can_add_member()


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Organization member with user and role info"""
    user = UserBasicSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    invited_by = UserBasicSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'id', 'organization', 'user', 'role', 'role_display',
            'can_manage_members', 'can_manage_repositories',
            'can_view_analytics', 'can_export_data',
            'joined_at', 'invited_by'
        ]
        read_only_fields = [
            'can_manage_members', 'can_manage_repositories',
            'can_view_analytics', 'can_export_data', 'joined_at'
        ]


class TeamSerializer(serializers.ModelSerializer):
    """Team serializer with member count"""
    organization = OrganizationSerializer(read_only=True)
    lead = UserBasicSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'organization', 'name', 'description',
            'lead', 'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()


class TeamMemberSerializer(serializers.ModelSerializer):
    """Team member serializer"""
    user = UserBasicSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    
    class Meta:
        model = TeamMember
        fields = ['id', 'team', 'user', 'joined_at']
        read_only_fields = ['joined_at']


class RepositoryAccessSerializer(serializers.ModelSerializer):
    """Repository access control serializer"""
    user = UserBasicSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    granted_by = UserBasicSerializer(read_only=True)
    access_level_display = serializers.CharField(
        source='get_access_level_display',
        read_only=True
    )
    
    class Meta:
        model = RepositoryAccess
        fields = [
            'id', 'repository', 'user', 'team',
            'access_level', 'access_level_display',
            'granted_at', 'granted_by'
        ]
        read_only_fields = ['granted_at', 'granted_by']


class AuditLogSerializer(serializers.ModelSerializer):
    """Audit log serializer for compliance"""
    user = UserBasicSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'organization', 'user', 'action', 'action_display',
            'resource_type', 'resource_id', 'resource_name',
            'details', 'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class OrganizationInviteSerializer(serializers.Serializer):
    """Serializer for inviting members to organization"""
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(
        choices=OrganizationMember.ROLE_CHOICES,
        default='developer'
    )
    
    def validate_email(self, value):
        """Check if user exists"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email does not exist"
            )
        return value
