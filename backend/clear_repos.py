#!/usr/bin/env python
"""
Script to clear all repositories from the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Repository, Commit, Issue, RepositoryWork, Collaboration, ActivityLog

def clear_all_repos():
    print("🗑️  Clearing all repository data...")
    
    # Delete all related data
    ActivityLog.objects.all().delete()
    print("✓ Deleted ActivityLogs")
    
    Collaboration.objects.all().delete()
    print("✓ Deleted Collaborations")
    
    RepositoryWork.objects.all().delete()
    print("✓ Deleted RepositoryWork")
    
    Issue.objects.all().delete()
    print("✓ Deleted Issues")
    
    Commit.objects.all().delete()
    print("✓ Deleted Commits")
    
    repo_count = Repository.objects.count()
    Repository.objects.all().delete()
    print(f"✓ Deleted {repo_count} Repositories")
    
    print("\n✅ All repository data cleared successfully!")
    print("📊 Current stats:")
    print(f"   - Repositories: {Repository.objects.count()}")
    print(f"   - Commits: {Commit.objects.count()}")
    print(f"   - Issues: {Issue.objects.count()}")

if __name__ == '__main__':
    clear_all_repos()
