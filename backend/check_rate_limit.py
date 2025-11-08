#!/usr/bin/env python
"""Check GitHub API rate limit status"""

import requests

def check_rate_limit():
    """Check GitHub API rate limit"""
    url = "https://api.github.com/rate_limit"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        core = data['rate']
        
        print("=== GitHub API Rate Limit Status ===")
        print(f"Limit: {core['limit']}")
        print(f"Remaining: {core['remaining']}")
        print(f"Used: {core['limit'] - core['remaining']}")
        
        if core['remaining'] == 0:
            import datetime
            reset_time = datetime.datetime.fromtimestamp(core['reset'])
            print(f"\n⚠️  RATE LIMIT EXCEEDED!")
            print(f"Resets at: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\nTo increase your rate limit to 5000/hour, use a GitHub token:")
            print("1. Go to https://github.com/settings/tokens")
            print("2. Click 'Generate new token (classic)'")
            print("3. Give it a name and select 'repo' scope")
            print("4. Copy the token and use it when importing repositories")
        else:
            print(f"\n✓ You have {core['remaining']} requests remaining")
    else:
        print(f"❌ Could not check rate limit: {response.status_code}")

if __name__ == "__main__":
    check_rate_limit()
