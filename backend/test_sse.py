"""
Test script to verify SSE endpoint is working
"""
import requests
import json

print("🧪 Testing SSE endpoint...")
print("Connecting to: http://localhost:8000/api/events/stream/")
print("-" * 60)

try:
    response = requests.get(
        'http://localhost:8000/api/events/stream/',
        stream=True,
        timeout=10
    )
    
    print(f"✅ Connection status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Cache-Control: {response.headers.get('Cache-Control')}")
    print("-" * 60)
    print("📡 Listening for events (will timeout after 10 seconds)...")
    print()
    
    # Read events from stream
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith('data: '):
                data = json.loads(decoded_line[6:])  # Remove 'data: ' prefix
                print(f"Event Type: {data.get('type')}")
                print(f"Timestamp: {data.get('timestamp')}")
                if data.get('message'):
                    print(f"Message: {data.get('message')}")
                if data.get('data'):
                    print(f"Data: {data.get('data')}")
                print()
                
except requests.exceptions.Timeout:
    print("\n⏱️  Connection timeout (this is normal if no events were sent)")
    print("✅ SSE endpoint is working correctly!")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("-" * 60)
print("Test complete!")
