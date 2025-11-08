"""
Test Release Readiness Score Feature
Quick validation script for hackathon demo
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_release_readiness():
    print("=" * 60)
    print("🚀 Testing Release Readiness Score Feature")
    print("=" * 60)
    
    # Test 1: Get score for repository 1
    print("\n📊 Test 1: Getting Release Readiness Score...")
    try:
        response = requests.get(f"{BASE_URL}/api/release-readiness/1/score/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Score: {data['score']}")
            print(f"   Level: {data['readiness_level']} {data['emoji']}")
            print(f"   Can Release: {data['can_release']}")
            print(f"   Blockers: {data['blockers_count']}")
            print(f"   Warnings: {data['warnings_count']}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get full report
    print("\n📋 Test 2: Getting Full Readiness Report...")
    try:
        response = requests.get(f"{BASE_URL}/api/release-readiness/1/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Repository: {data['repository']['name']}")
            print(f"   Score: {data['score']}/100")
            print(f"   Recommendation: {data['recommendation']}")
            print(f"   Blockers: {len(data['blockers'])}")
            print(f"   Warnings: {len(data['warnings'])}")
            print(f"   Passed Checks: {len(data['passed_checks'])}")
            
            if data['blockers']:
                print("\n   🚫 Blocking Issues:")
                for blocker in data['blockers'][:3]:
                    print(f"      {blocker}")
            
            if data['warnings']:
                print("\n   ⚠️ Warnings:")
                for warning in data['warnings'][:3]:
                    print(f"      {warning}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get blockers only
    print("\n🚫 Test 3: Getting Blockers...")
    try:
        response = requests.get(f"{BASE_URL}/api/release-readiness/1/blockers/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Has Blockers: {data['has_blockers']}")
            print(f"   Blocker Count: {data['blockers_count']}")
            print(f"   Warning Count: {data['warnings_count']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get trend
    print("\n📈 Test 4: Getting Readiness Trend...")
    try:
        response = requests.get(f"{BASE_URL}/api/release-readiness/1/trend/?days=30")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current Score: {data['current_score']}")
            print(f"   Trend Direction: {data['trend_direction']}")
            print(f"   Data Points: {len(data['trend'])}")
            if len(data['trend']) >= 2:
                print(f"   Change: {data['trend'][-1]['score'] - data['trend'][0]['score']:.1f} points")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Get dashboard
    print("\n📊 Test 5: Getting Dashboard Data...")
    try:
        response = requests.get(f"{BASE_URL}/api/release-readiness/1/dashboard/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current Score: {data['current']['score']}")
            print(f"   Readiness Level: {data['current']['readiness_level']['label']}")
            print(f"   Action Items Categories: {len(data['action_items']['next_steps'])}")
            print(f"   Trend Direction: {data['trend']['trend_direction']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Get all repositories
    print("\n🗂️ Test 6: Getting All Repositories Readiness...")
    try:
        response = requests.get(f"{BASE_URL}/api/release-readiness/all/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total Repositories: {data['total_count']}")
            print(f"   Ready to Release: {data['ready_to_release_count']}")
            print(f"   Average Score: {data['average_score']}")
            
            if data['repositories']:
                print("\n   Top 3 Repositories:")
                for repo in data['repositories'][:3]:
                    print(f"      {repo['name']}: {repo['score']:.1f} {repo['emoji']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All Tests Completed!")
    print("=" * 60)

if __name__ == "__main__":
    print("\n🎯 Release Readiness Score Test Suite")
    print("Make sure the Django server is running on port 8000\n")
    
    test_release_readiness()
