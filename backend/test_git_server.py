"""
Test script for Git server functionality
Run this after starting the backend server to verify everything works
"""

import requests
import json
import os
import subprocess
import shutil
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "testuser"
TEST_REPO = "test-project"
TEST_DIR = Path(__file__).parent / "test_git_repo"

# Get auth token (you need to set this)
TOKEN = os.environ.get("LAZYSHEEPS_TOKEN", "")

if not TOKEN:
    print("❌ Error: Please set LAZYSHEEPS_TOKEN environment variable")
    print("   Get your token by logging in via the web UI")
    print("   Then run: $env:LAZYSHEEPS_TOKEN='your_token_here'")
    exit(1)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_create_repository():
    """Test repository creation"""
    print("\n🧪 Test 1: Create Repository")
    print("-" * 50)
    
    data = {
        "name": TEST_REPO,
        "description": "Test repository for Git server"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/git/create/",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        print("✅ Repository created successfully!")
        print(f"   Name: {result['repository']['name']}")
        print(f"   Clone URL: {result['repository']['clone_url']}")
        return result['repository']
    else:
        print(f"❌ Failed to create repository: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_list_repositories():
    """Test listing user repositories"""
    print("\n🧪 Test 2: List Repositories")
    print("-" * 50)
    
    response = requests.get(
        f"{BASE_URL}/api/git/{TEST_USERNAME}/repositories/",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result['repositories'])} repositories")
        for repo in result['repositories']:
            print(f"   - {repo['name']}: {repo.get('description', 'No description')}")
        return result['repositories']
    else:
        print(f"❌ Failed to list repositories: {response.status_code}")
        return []

def test_git_operations():
    """Test actual Git push/pull operations"""
    print("\n🧪 Test 3: Git Operations")
    print("-" * 50)
    
    # Clean up test directory if exists
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    
    # Create test directory
    TEST_DIR.mkdir()
    os.chdir(TEST_DIR)
    
    try:
        # Initialize Git repo
        print("   📝 Initializing Git repository...")
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        
        # Create test files
        print("   📄 Creating test files...")
        with open("README.md", "w") as f:
            f.write("# Test Project\n\nThis is a test repository.\n")
        
        with open("test.txt", "w") as f:
            f.write("Hello from LazySheeps Git Server!\n")
        
        # Stage and commit
        print("   💾 Committing files...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        
        # Rename branch to main if needed
        try:
            subprocess.run(["git", "branch", "-M", "main"], check=True, capture_output=True)
        except:
            pass
        
        # Add remote
        print("   🔗 Adding remote...")
        remote_url = f"{BASE_URL}/git/{TEST_USERNAME}/{TEST_REPO}.git"
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
        
        # Push to server
        print("   ⬆️  Pushing to server...")
        result = subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Git push successful!")
            return True
        else:
            print("❌ Git push failed:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    finally:
        os.chdir(Path(__file__).parent)

def test_browse_repository():
    """Test repository browsing"""
    print("\n🧪 Test 4: Browse Repository")
    print("-" * 50)
    
    response = requests.get(
        f"{BASE_URL}/api/git/{TEST_USERNAME}/{TEST_REPO}/browse/",
        headers=headers,
        params={"path": "/"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Repository browsing works!")
        print(f"   Files found: {len(result['items'])}")
        for item in result['items']:
            print(f"   - {item['name']} ({item['type']})")
        return True
    else:
        print(f"❌ Failed to browse repository: {response.status_code}")
        return False

def test_view_file():
    """Test file viewing"""
    print("\n🧪 Test 5: View File Content")
    print("-" * 50)
    
    response = requests.get(
        f"{BASE_URL}/api/git/{TEST_USERNAME}/{TEST_REPO}/file/",
        headers=headers,
        params={"path": "README.md"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ File viewing works!")
        print(f"   File: {result['file']['name']}")
        print(f"   Size: {result['file']['size']} bytes")
        print(f"   Content preview:")
        print("   " + "\n   ".join(result['file']['content'][:5]))
        return True
    else:
        print(f"❌ Failed to view file: {response.status_code}")
        return False

def test_commit_history():
    """Test commit history retrieval"""
    print("\n🧪 Test 6: Commit History")
    print("-" * 50)
    
    response = requests.get(
        f"{BASE_URL}/api/git/{TEST_USERNAME}/{TEST_REPO}/commits/",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Commit history works!")
        print(f"   Commits found: {len(result['commits'])}")
        for commit in result['commits'][:3]:
            print(f"   - {commit['sha'][:7]}: {commit['message']} by {commit['author']}")
        return True
    else:
        print(f"❌ Failed to get commit history: {response.status_code}")
        return False

def cleanup():
    """Clean up test artifacts"""
    print("\n🧹 Cleaning up...")
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    print("✅ Cleanup complete")

def main():
    """Run all tests"""
    print("=" * 50)
    print("🚀 LazySheeps Git Server Test Suite")
    print("=" * 50)
    
    results = []
    
    # Test 1: Create repository
    repo = test_create_repository()
    results.append(("Create Repository", repo is not None))
    
    # Test 2: List repositories
    repos = test_list_repositories()
    results.append(("List Repositories", len(repos) > 0))
    
    # Test 3: Git operations
    git_success = test_git_operations()
    results.append(("Git Push/Pull", git_success))
    
    # Test 4: Browse repository
    browse_success = test_browse_repository()
    results.append(("Browse Repository", browse_success))
    
    # Test 5: View file
    view_success = test_view_file()
    results.append(("View File", view_success))
    
    # Test 6: Commit history
    history_success = test_commit_history()
    results.append(("Commit History", history_success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Git server is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    # Cleanup
    cleanup()

if __name__ == "__main__":
    main()
