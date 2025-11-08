"""
Script to manually sync a repository and fetch all contributors
"""
import sys
import os
import django

# Add the backend directory to the Python path
backend_dir = r'C:\Users\ayush\OneDrive\Desktop\LazySheeps\backend'
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Repository, Contributor, RepositoryWork
from api.github_importer import GitHubImporter

print("=" * 60)
print("Syncing LazySheeps repository...")
print("=" * 60)

try:
    repo = Repository.objects.get(id=4)
    print(f"\n✅ Found repository: {repo.name}")
    print(f"   GitHub URL: {repo.url}")
    
    # Extract owner and repo name from URL
    url_parts = repo.url.rstrip('/').split('/')
    owner = url_parts[-2]
    repo_name = url_parts[-1]
    
    print(f"\n🔄 Fetching data from GitHub...")
    print(f"   Owner: {owner}")
    print(f"   Repo: {repo_name}")
    
    # Re-import the repository using GitHubImporter
    importer = GitHubImporter(github_token=None)  # Will use app if available
    result = importer.import_repository(f"https://github.com/{owner}/{repo_name}")
    
    if result.get('status') == 'success':
        print(f"\n✅ Sync completed successfully!")
        print(f"   {result.get('message', '')}")
        
        # Show contributors
        print(f"\n📊 Contributors in database:")
        contributors = Contributor.objects.all()
        for c in contributors:
            works_count = c.works.count()
            print(f"   - {c.username} ({c.github_id}): {works_count} repository works")
            for work in c.works.all():
                commits = work.commits.count()
                issues = work.issues.count()
                print(f"      └─ {work.repository.name}: {commits} commits, {issues} issues")
        
        print(f"\n🎉 Total contributors: {contributors.count()}")
    else:
        print(f"\n❌ Sync failed: {result.get('error', 'Unknown error')}")
        
except Repository.DoesNotExist:
    print("\n❌ Repository with ID 4 not found in database!")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
