#!/usr/bin/env python3
"""
Simple script to get Anytype API key.
Makes two POST requests to get a display code, then exchange it for an API key.
"""

import json
import httpx


def create_challenge(base_url, app_name):
    """Step 1: Create challenge to get display code"""
    response = httpx.post(
        f"{base_url}/v1/auth/challenges",
        json={"app_name": app_name},
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()


def create_api_key(base_url, challenge_id, code):
    """Step 2: Exchange challenge for API key"""
    response = httpx.post(
        f"{base_url}/v1/auth/api_keys",
        json={"challenge_id": challenge_id, "code": code},
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()


def main():
    base_url = input("API URL (default: http://localhost:31009): ").strip() or "http://localhost:31009"
    app_name = input("App name (default: API Client): ").strip() or "API Client"
    
    # Step 1: Get display code
    print("\nGetting display code...")
    challenge = create_challenge(base_url, app_name)
    display_code = challenge["display_code"]
    challenge_id = challenge["challenge_id"]
    
    print(f"Display code: {display_code}")
    print("Enter this code in Anytype (Settings > Account)")
    input("Press Enter when done...")
    
    # Step 2: Get API key
    print("Getting API key...")
    result = create_api_key(base_url, challenge_id, display_code)
    api_key = result["token"]
    
    print(f"\nAPI Key: {api_key}")
    print(f"Export command: export ANYTYPE_API_KEY={api_key}")


if __name__ == "__main__":
    main()