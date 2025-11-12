#!/usr/bin/env python3
"""
Simple test script for the Weather API
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_weather_api():
    print("🌤️  Testing Weather API")
    print("=" * 40)

    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python app.py")
        return

    # Test 2: API info
    print("\n2. Testing API info...")
    response = requests.get(BASE_URL)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Valid city
    print("\n3. Testing valid city (London)...")
    data = {"city": "London"}
    response = requests.post(f"{BASE_URL}/weather", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 4: Another valid city
    print("\n4. Testing another city (New York)...")
    data = {"city": "New York"}
    response = requests.post(f"{BASE_URL}/weather", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 5: Invalid city
    print("\n5. Testing invalid city...")
    data = {"city": "InvalidCityName123"}
    response = requests.post(f"{BASE_URL}/weather", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 6: Missing city parameter
    print("\n6. Testing missing city parameter...")
    response = requests.post(f"{BASE_URL}/weather", json={})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\n✅ Testing complete!")

if __name__ == "__main__":
    test_weather_api()