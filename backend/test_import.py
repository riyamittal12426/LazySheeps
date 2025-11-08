#!/usr/bin/env python
"""Test script to verify GitHub import with detailed commits"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.github_fetcher import GitHubFetcher
from api.github_importer import GitHubImporter
from api.models import Repository, Contributor, Commit

# Clear existing data
print("Clearing existing data...")
Commit.objects.all().delete()
Repository.objects.all().delete()
Contributor.objects.all().delete()
print("✓ Data cleared\n")

# Test GitHub import
print("Testing GitHub import...")
repo_url = "https://github.com/AyushChoudhary6/biomarine-ai"
importer = GitHubImporter()

try:
    result = importer.import_repository(repo_url)
    print("\n=== Import Result ===")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if 'stats' in result:
        print(f"Stats: {result['stats']}")
    
    # Check commits in database
    print("\n=== Database Check ===")
    repos = Repository.objects.count()
    contributors = Contributor.objects.count()
    commits = Commit.objects.count()
    print(f"Repositories: {repos}")
    print(f"Contributors: {contributors}")
    print(f"Commits: {commits}")
    
    if commits > 0:
        print("\n=== Sample Commits ===")
        for commit in Commit.objects.all()[:5]:
            print(f"  - {commit.summary[:50]}... | +{commit.additions} -{commit.deletions} | churn: {commit.code_churn_ratio:.2f}")
    else:
        print("\n⚠ WARNING: No commits imported!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
