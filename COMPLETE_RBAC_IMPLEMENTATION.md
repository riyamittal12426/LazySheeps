# Complete RBAC & Multi-Tenant Implementation

## Current Status: 70% Complete ✅

### ✅ What's Complete:
1. **Backend Models (100%)** - All 6 models implemented
2. **Database Migrations (100%)** - All tables created with indexes
3. **Documentation (100%)** - Setup guides and implementation docs

### ❌ What's Missing (30%):
1. **API Layer** - Serializers and ViewSets
2. **Frontend Components** - UI for organization management
3. **Permission Enforcement** - Middleware and decorators

---

## Step 1: Create RBAC Serializers (10 mins)

Create `backend/api/rbac_serializers.py`:

```python
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
```

---

## Step 2: Create RBAC ViewSets (15 mins)

Create `backend/api/rbac_views.py`:

```python
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
    RepositoryAccess, AuditLog, User
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
```

---

## Step 3: Register API Routes (5 mins)

Update `backend/config/urls.py`:

```python
from rest_framework.routers import DefaultRouter
from api.rbac_views import (
    OrganizationViewSet,
    TeamViewSet,
    AuditLogViewSet
)

# Create router
router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    # ... existing patterns ...
    
    # RBAC API
    path('api/', include(router.urls)),
]
```

---

## Step 4: Test API Endpoints (10 mins)

```bash
# 1. Create organization
curl -X POST http://localhost:8000/api/organizations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Company",
    "slug": "my-company",
    "plan": "pro"
  }'

# 2. Invite member
curl -X POST http://localhost:8000/api/organizations/1/invite_member/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teammate@example.com",
    "role": "developer"
  }'

# 3. List members
curl http://localhost:8000/api/organizations/1/members/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. View audit logs
curl http://localhost:8000/api/audit-logs/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Step 5: Frontend Components (Optional, 30 mins)

Create React components:

### `frontend/src/components/OrganizationSelector.jsx`
```jsx
import { useState, useEffect } from 'react';

export default function OrganizationSelector() {
  const [organizations, setOrganizations] = useState([]);
  const [selected, setSelected] = useState(null);
  
  useEffect(() => {
    fetch('/api/organizations/', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(res => res.json())
      .then(data => {
        setOrganizations(data);
        if (data.length > 0) setSelected(data[0].id);
      });
  }, []);
  
  return (
    <div className="org-selector">
      <select
        value={selected || ''}
        onChange={(e) => setSelected(Number(e.target.value))}
        className="form-select"
      >
        {organizations.map(org => (
          <key={org.id} value={org.id}>
            {org.name} ({org.plan})
          </option>
        ))}
      </select>
    </div>
  );
}
```

---

## ✅ Completion Checklist

- [ ] Create `backend/api/rbac_serializers.py`
- [ ] Create `backend/api/rbac_views.py`
- [ ] Update `backend/config/urls.py` with router
- [ ] Test API endpoints with curl
- [ ] Create frontend `OrganizationSelector.jsx`
- [ ] Create frontend `InviteMemberModal.jsx`
- [ ] Add permission checks to existing views
- [ ] Deploy and test end-to-end

---

## 🎯 Expected Outcome

After completing these steps, you will have:
- ✅ Full RBAC API with 15+ endpoints
- ✅ Organization and team management
- ✅ Role-based permission enforcement
- ✅ Audit logging for compliance
- ✅ Frontend components for multi-tenancy

**Total Implementation Time: ~70 minutes**
