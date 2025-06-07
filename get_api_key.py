#!/usr/bin/env python3
"""
Simple script to get Anytype API key.
Makes two POST requests to get a display code, then exchange it for an API key.
"""

import httpx


def create_challenge(base_url, app_name):
    """Step 1: Create a challenge to get display code"""
    response = httpx.post(
        f"{base_url}/v1/auth/challenges",
        json={"app_name": app_name},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    return response.json()


def create_api_key(base_url, challenge_id, code):
    """Step 2: Exchange challenge for an API key"""
    response = httpx.post(
        f"{base_url}/v1/auth/api_keys",
        json={"challenge_id": challenge_id, "code": code},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    return response.json()


def main():
    base_url = (
        input("API URL (default: http://localhost:31009): ").strip()
        or "http://localhost:31009"
    )
    app_name = input("App name (default: API Client): ").strip() or "API Client"

    # Step 1: Create a challenge
    print("\nCreating challenge...")
    challenge = create_challenge(base_url, app_name)
    challenge_id = challenge["challenge_id"]

    # Step 2: Get an API key
    print("Getting API key...")
    code = input("Enter the code from Anytype: ").strip()
    result = create_api_key(base_url, challenge_id, code)
    api_key = result["api_key"]

    print(f"\nAPI Key: {api_key}")
    print(f"Export command: export ANYTYPE_API_KEY={api_key}")


if __name__ == "__main__":
    main()
