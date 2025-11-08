from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Repository, Issue, Commit, RepositoryWork, Contributor, Badge, Collaboration, ActivityLog, User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 
                 'avatar_url', 'github_username', 'github_url', 'location', 
                 'website', 'company', 'total_repositories', 'total_commits', 
                 'total_contributions', 'date_joined', 'created_at', 'updated_at']
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')
        
        attrs['user'] = user
        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'avatar_url', 
                 'github_username', 'github_url', 'location', 'website', 'company']

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'

class CommitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commit
        fields = '__all__'

class RepositorySerializer(serializers.ModelSerializer):
    contributor_count = serializers.SerializerMethodField()
    recent_activity = serializers.SerializerMethodField()
    
    class Meta:
        model = Repository
        fields = '__all__'
    
    def get_contributor_count(self, obj):
        return obj.works.values('contributor').distinct().count()
    
    def get_recent_activity(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return obj.commits.filter(committed_at__gte=thirty_days_ago).count()

class BadgeSerializer(serializers.ModelSerializer):
    badge_name = serializers.CharField(source='get_badge_type_display', read_only=True)
    
    class Meta:
        model = Badge
        fields = ['id', 'badge_type', 'badge_name', 'earned_date', 'description']

class RepositoryWorkSerializer(serializers.ModelSerializer):
    issues = IssueSerializer(many=True, read_only=True)
    commits = CommitSerializer(many=True, read_only=True)
    repository_name = serializers.CharField(source='repository.name', read_only=True)

    class Meta:
        model = RepositoryWork
        fields = '__all__'

class ContributorSerializer(serializers.ModelSerializer):
    works = RepositoryWorkSerializer(many=True, read_only=True)
    badges = BadgeSerializer(many=True, read_only=True)
    badge_count = serializers.SerializerMethodField()
    next_level_xp = serializers.SerializerMethodField()
    
    class Meta:
        model = Contributor
        fields = '__all__'
    
    def get_badge_count(self, obj):
        return obj.badges.count()
    
    def get_next_level_xp(self, obj):
        next_level = obj.level + 1
        required_xp = next_level * 1000
        return required_xp - obj.experience_points

class CollaborationSerializer(serializers.ModelSerializer):
    contributor_1_name = serializers.CharField(source='contributor_1.username', read_only=True)
    contributor_2_name = serializers.CharField(source='contributor_2.username', read_only=True)
    repository_name = serializers.CharField(source='repository.name', read_only=True)
    
    class Meta:
        model = Collaboration
        fields = '__all__'

class ActivityLogSerializer(serializers.ModelSerializer):
    contributor_name = serializers.CharField(source='contributor.username', read_only=True)
    contributor_avatar = serializers.URLField(source='contributor.avatar_url', read_only=True)
    repository_name = serializers.CharField(source='repository.name', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = '__all__'

class DataSerializer(serializers.Serializer):
    repositories = RepositorySerializer(many=True, read_only=True)
    contributors = ContributorSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        # Assuming 'instance' is not a single object but a way to access all data.
        # This serializer might need to be used differently, perhaps in a view
        # where you explicitly pass the querysets.
        return {
            'repositories': RepositorySerializer(Repository.objects.all(), many=True).data,
            'contributors': ContributorSerializer(Contributor.objects.all(), many=True).data
        }

    # If this serializer is meant to serialize a specific object that holds
    # references to all repositories and contributors, the implementation
    # would need to change based on that object's structure.
    # For now, it assumes it will be instantiated without an instance and
    # will fetch all data directly.