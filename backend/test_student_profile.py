#!/usr/bin/env python3
"""
Test script for student profile with alerts and interventions
"""
import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:5001/api"

# Test data
TEST_USER = {"email": "test_coach@example.com", "password": "password123"}

TEST_STUDENT_ID = 2  # Change this to an actual student ID


def login():
    """Login and get access token"""
    response = requests.post(f"{BASE_URL}/auth/login", json=TEST_USER)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None


def get_student_profile(token, student_id):
    """Get student profile"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/reports/profile/{student_id}", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get profile: {response.text}")
        return None


def main():
    """Main test function"""
    print("Testing Student Profile with Alerts and Interventions")
    print("=" * 50)

    # Login
    print("\n1. Logging in...")
    token = login()
    if not token:
        print("Failed to login")
        return
    print("✓ Login successful")

    # Get student profile
    print(f"\n2. Getting profile for student ID {TEST_STUDENT_ID}...")
    profile = get_student_profile(token, TEST_STUDENT_ID)

    if profile:
        print("✓ Profile retrieved successfully")

        # Display AI analysis
        ai_analysis = profile.get("ai_analysis", {})

        # Display alerts
        alerts = ai_analysis.get("alerts", [])
        print(f"\n3. Alerts ({len(alerts)} found):")
        for alert in alerts:
            print(f"   - [{alert['type'].upper()}] {alert['message']} (Priority: {alert['priority']})")

        # Display interventions
        interventions = ai_analysis.get("interventions", [])
        print(f"\n4. Interventions ({len(interventions)} found):")
        for intervention in interventions:
            print(f"\n   {intervention['title']}")
            print(f"   Type: {intervention['type']} | Priority: {intervention['priority']}")
            print(f"   Description: {intervention['description']}")
            print(f"   Expected Impact: {intervention['expected_impact']}")
            print(f"   Timeline: {intervention['timeline']}")
            print(f"   Action Items:")
            for item in intervention.get("action_items", []):
                print(f"      - {item}")

        # Display other key metrics
        scores = profile.get("development_scores", {})
        print(f"\n5. Key Metrics:")
        print(f"   - Performance Index: {scores.get('performance_index', 0)}")
        print(f"   - Risk Score: {scores.get('risk_score', 'Unknown')}")
        print(f"   - Engagement Score: {scores.get('engagement_score', 0)}")
        print(f"   - Motivation Level: {ai_analysis.get('motivation_level', 'Unknown')}")

        # Save full profile to file for inspection
        with open("student_profile_test.json", "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        print("\n✓ Full profile saved to student_profile_test.json")
    else:
        print("✗ Failed to retrieve profile")


if __name__ == "__main__":
    main()
