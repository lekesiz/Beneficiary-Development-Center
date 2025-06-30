#!/usr/bin/env python3
"""Test script to verify health endpoints work without JSON decode errors."""

import requests
import json

# Base URL - adjust if running on different port
BASE_URL = "http://localhost:5001"

def test_endpoint(method, path, data=None, headers=None):
    """Test an endpoint and print results."""
    url = f"{BASE_URL}{path}"
    print(f"\n{'='*60}")
    print(f"Testing: {method} {path}")
    print(f"URL: {url}")
    
    if headers:
        print(f"Headers: {headers}")
    if data:
        print(f"Data: {data}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.request(method, url, json=data, headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Try to parse JSON response
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
        except:
            print(f"Response (text): {response.text[:500]}")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Test various endpoints."""
    print("Testing BDC Backend Health Endpoints")
    print("Make sure the backend is running on port 5001")
    
    # Test health endpoints
    test_endpoint("GET", "/health")
    test_endpoint("GET", "/health/detailed")
    test_endpoint("GET", "/health/readiness")
    test_endpoint("GET", "/health/liveness")
    test_endpoint("GET", "/metrics")
    
    # Test API endpoints without auth (should get 401 but not JSON decode error)
    test_endpoint("GET", "/api/v1/users")
    test_endpoint("GET", "/api/v1/beneficiaries")
    
    # Test with empty POST request (should get proper error, not JSON decode error)
    test_endpoint("POST", "/api/v1/auth/login")
    
    # Test with valid JSON POST
    test_endpoint("POST", "/api/v1/auth/login", data={"email": "test@example.com", "password": "test"})

if __name__ == "__main__":
    main()