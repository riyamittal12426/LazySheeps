"""
Test script for Auto-Triage and ChatBot features
Run this to test the functionality without GitHub webhooks
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_auto_triage():
    """Test auto-triage functionality"""
    print("\n" + "="*60)
    print("🤖 Testing Auto-Triage & Labeling")
    print("="*60)
    
    # Test 1: Classify Issue
    print("\n1️⃣ Testing Issue Classification...")
    
    issue_data = {
        "title": "Login form shows error 500 when invalid credentials entered",
        "body": """
        When users enter wrong password, instead of showing a friendly error message,
        the form crashes with HTTP 500 error. Stack trace shows:
        
        File "views.py", line 42, in login_view
            user = authenticate(username=username, password=password)
        
        This is a critical bug affecting user experience.
        """,
        "labels": []
    }
    
    response = requests.post(
        f"{BASE_URL}/api/triage/classify/",
        json=issue_data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            classification = result['classification']
            print(f"✅ Classification successful!")
            print(f"   Type: {classification['type']}")
            print(f"   Component: {classification['component']}")
            print(f"   Priority: {classification['priority']}")
            print(f"   Confidence: {classification['confidence']:.0%}")
            print(f"   Reasoning: {classification['reasoning']}")
            print(f"   Complexity: {classification['complexity']}")
            print(f"   Estimated Effort: {classification['estimated_effort']} hours")
        else:
            print(f"❌ Error: {result.get('error')}")
    else:
        print(f"❌ Request failed: {response.status_code}")
    
    # Test 2: Full Triage (requires repository in DB)
    print("\n2️⃣ Testing Full Triage (requires repository ID)...")
    print("   Skipping - requires valid repository_id from database")
    print("   Use the UI component to test this feature")


def test_chatbot():
    """Test chatbot functionality"""
    print("\n" + "="*60)
    print("💬 Testing Slack/Discord Bot")
    print("="*60)
    
    # Test 1: Team Health
    print("\n1️⃣ Testing Team Health...")
    
    response = requests.get(f"{BASE_URL}/api/chatbot/team-health/")
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Team health retrieved!")
            print("\nReport Preview:")
            print("-" * 60)
            print(result['report'][:500] + "...")
        else:
            print(f"❌ Error: {result.get('error')}")
    else:
        print(f"❌ Request failed: {response.status_code}")
    
    # Test 2: Daily Digest
    print("\n2️⃣ Testing Daily Digest...")
    
    response = requests.get(f"{BASE_URL}/api/chatbot/daily-digest/")
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Daily digest generated!")
            print("\nDigest Preview:")
            print("-" * 60)
            print(result['digest'][:500] + "...")
        else:
            print(f"❌ Error: {result.get('error')}")
    else:
        print(f"❌ Request failed: {response.status_code}")
    
    # Test 3: Risk Alerts
    print("\n3️⃣ Testing Risk Alerts...")
    
    response = requests.get(f"{BASE_URL}/api/chatbot/risk-alerts/")
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Risk alerts generated!")
            print("\nRisk Report:")
            print("-" * 60)
            print(result['risks'])
        else:
            print(f"❌ Error: {result.get('error')}")
    else:
        print(f"❌ Request failed: {response.status_code}")
    
    # Test 4: PR Summary (requires GitHub token)
    print("\n4️⃣ Testing PR Summary...")
    print("   Skipping - requires valid GitHub token and PR")
    print("   Use the UI component to test this feature")


def test_chatbot_commands():
    """Test chatbot command interface"""
    print("\n" + "="*60)
    print("🎮 Testing ChatBot Commands")
    print("="*60)
    
    commands = [
        {
            "name": "Team Health",
            "command": "team-health",
            "args": []
        },
        {
            "name": "Daily Digest",
            "command": "digest",
            "args": []
        },
        {
            "name": "Risk Alerts",
            "command": "risks",
            "args": []
        }
    ]
    
    for cmd in commands:
        print(f"\n📝 Testing: {cmd['name']}")
        
        response = requests.post(
            f"{BASE_URL}/api/chatbot/command/",
            json={
                "platform": "slack",
                "command": cmd["command"],
                "args": cmd["args"]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Command executed successfully!")
                print(f"   Response: {result['response'][:100]}...")
            else:
                print(f"❌ Error: {result.get('error')}")
        else:
            print(f"❌ Request failed: {response.status_code}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 Katalyst Auto-Triage & ChatBot Tests")
    print("="*60)
    print("\nMake sure Django server is running on http://localhost:8000")
    print("Press Enter to continue...")
    input()
    
    try:
        # Test auto-triage
        test_auto_triage()
        
        # Test chatbot
        test_chatbot()
        
        # Test chatbot commands
        test_chatbot_commands()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        print("\n📌 Next Steps:")
        print("1. Test the frontend components at http://localhost:5173")
        print("2. Configure GitHub webhooks for auto-triage")
        print("3. Set up Slack/Discord webhooks")
        print("4. Add environment variables to .env")
        print("\nSee AUTO_TRIAGE_CHATBOT_GUIDE.md for full setup instructions")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to Django server")
        print("Make sure the server is running: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
