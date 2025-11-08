#!/usr/bin/env python
"""Test script to verify Llama API connection"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

api_key = os.getenv('LLAMA_API_KEY')
print(f"API Key loaded: {api_key[:20]}..." if api_key else "API Key NOT loaded")

# Test with different base URLs and model names
test_configs = [
    {"base_url": "https://api.llama.com/v1", "model": "meta-llama/Llama-3.3-70B-Instruct"},
    {"base_url": "https://api.llama.com/v1", "model": "llama3.3-70b-instruct"},
    {"base_url": "https://api.llama.com/v1", "model": "Llama-3.3-70B-Instruct"},
    {"base_url": "https://api.llama.com", "model": "meta-llama/Llama-3.3-70B-Instruct"},
]

for config in test_configs:
    base_url = config["base_url"]
    model = config["model"]
    print(f"\n{'='*60}")
    print(f"Testing with:")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    print(f"{'='*60}")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Try to make a simple request
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello, test message."}],
            max_tokens=10
        )
        
        print(f"✓ SUCCESS! Connection works!")
        print(f"  Base URL: {base_url}")
        print(f"  Model: {model}")
        print(f"Response: {response.choices[0].message.content}")
        break
        
    except Exception as e:
        print(f"✗ FAILED")
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")

print(f"\n{'='*60}")
print("Test complete")
print(f"{'='*60}")
