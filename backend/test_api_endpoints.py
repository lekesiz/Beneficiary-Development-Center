#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all backend API endpoints to ensure they are working correctly
"""

import requests
import json
import time
import sys
from typing import Dict, List, Tuple, Optional

# Base configuration
BASE_URL = "http://localhost:5001"
TENANT_ID = "1"

# Test credentials
TEST_CREDENTIALS = {
    "email": "admin@bdc.local",
    "password": "admin123"
}

# ANSI color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str = Colors.END):
    """Print colored text"""
    print(f"{color}{text}{Colors.END}")

def print_test_header(endpoint: str, method: str):
    """Print test header"""
    print(f"\n{Colors.BOLD}Testing: {method} {endpoint}{Colors.END}")

def print_result(success: bool, message: str):
    """Print test result"""
    if success:
        print_colored(f"✓ {message}", Colors.GREEN)
    else:
        print_colored(f"✗ {message}", Colors.RED)

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json",
            "X-Tenant-ID": TENANT_ID
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def test_endpoint(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     expected_status: int = 200, description: str = "") -> Tuple[bool, str]:
        """Test a single endpoint"""
        print_test_header(endpoint, method)
        
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == "GET":
                response = self.session.get(url, headers=self.get_headers())
            elif method == "POST":
                response = self.session.post(url, headers=self.get_headers(), json=data)
            elif method == "PUT":
                response = self.session.put(url, headers=self.get_headers(), json=data)
            elif method == "DELETE":
                response = self.session.delete(url, headers=self.get_headers())
            else:
                return False, f"Unsupported method: {method}"
            
            success = response.status_code == expected_status
            
            if success:
                message = f"Status: {response.status_code} - {description or 'Success'}"
            else:
                message = f"Status: {response.status_code} (Expected: {expected_status}) - {response.text[:200]}"
            
            print_result(success, message)
            
            # Store result
            self.test_results.append({
                "endpoint": endpoint,
                "method": method,
                "success": success,
                "status_code": response.status_code,
                "expected_status": expected_status
            })
            
            return success, response.json() if response.content else {}
            
        except Exception as e:
            message = f"Error: {str(e)}"
            print_result(False, message)
            self.test_results.append({
                "endpoint": endpoint,
                "method": method,
                "success": False,
                "error": str(e)
            })
            return False, {}
    
    def run_tests(self):
        """Run all API tests"""
        print_colored("\n" + "="*60, Colors.BOLD)
        print_colored("BDC API Endpoint Testing", Colors.BOLD)
        print_colored("="*60 + "\n", Colors.BOLD)
        
        # 1. Test Authentication
        print_colored("\n1. AUTHENTICATION ENDPOINTS", Colors.BLUE)
        
        # Login
        success, data = self.test_endpoint(
            "POST", "/api/v1/auth/login", 
            TEST_CREDENTIALS, 
            description="User login"
        )
        
        if success and "access_token" in data:
            self.token = data["access_token"]
            print_colored(f"   Token obtained: {self.token[:20]}...", Colors.YELLOW)
        
        # Get current user
        self.test_endpoint("GET", "/api/v1/auth/me", description="Get current user")
        
        # Refresh token
        if success and "refresh_token" in data:
            # Store current token
            current_token = self.token
            # Use refresh token as bearer token
            self.token = data["refresh_token"]
            self.test_endpoint(
                "POST", "/api/v1/auth/refresh",
                None,
                description="Refresh token"
            )
            # Restore access token
            self.token = current_token
        
        # 2. Test User Management
        print_colored("\n2. USER MANAGEMENT ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/users", description="List users")
        self.test_endpoint("GET", "/api/v1/users/1", description="Get user by ID")
        
        # 3. Test Beneficiaries
        print_colored("\n3. BENEFICIARY ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/beneficiaries", description="List beneficiaries")
        self.test_endpoint("GET", "/api/v1/beneficiaries/1", description="Get beneficiary by ID")
        
        # 4. Test Programs
        print_colored("\n4. PROGRAM ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/programs", description="List programs")
        success, programs = self.test_endpoint("GET", "/api/v1/programs?limit=1", description="Get first program")
        
        if success and programs.get("programs"):
            program_id = programs["programs"][0]["id"]
            self.test_endpoint("GET", f"/api/v1/programs/{program_id}", description="Get program by ID")
            self.test_endpoint("GET", f"/api/v1/programs/{program_id}/courses", description="Get program courses")
        
        # 5. Test Courses
        print_colored("\n5. COURSE ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/courses", description="List courses")
        self.test_endpoint("GET", "/api/v1/courses/1", description="Get course by ID")
        
        # 6. Test Evaluations
        print_colored("\n6. EVALUATION ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/evaluations", description="List evaluations")
        self.test_endpoint("GET", "/api/v1/evaluations/1/statistics", description="Get evaluation statistics")
        
        # 7. Test Learning Paths
        print_colored("\n7. LEARNING PATH ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/learning-paths/my-paths", description="Get my learning paths")
        
        # 8. Test Coach Notes
        print_colored("\n8. COACH NOTES ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/coach-notes", description="List coach notes")
        self.test_endpoint("GET", "/api/v1/coach-notes/categories", description="Get note categories")
        self.test_endpoint("GET", "/api/v1/coach-notes/priorities", description="Get note priorities")
        
        # 9. Test Reports
        print_colored("\n9. REPORT ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/reports", description="List reports")
        self.test_endpoint("GET", "/api/v1/reports/overview", description="Get reports overview")
        
        # 10. Test Dashboard
        print_colored("\n10. DASHBOARD ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/dashboard/stats", description="Get dashboard stats")
        self.test_endpoint("GET", "/api/v1/dashboard/activity", description="Get recent activity")
        
        # 11. Test Analytics
        print_colored("\n11. ANALYTICS ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/analytics/overview", description="Get analytics overview")
        
        # 12. Test Notifications
        print_colored("\n12. NOTIFICATION ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/api/v1/notifications", description="List notifications")
        self.test_endpoint("GET", "/api/v1/notifications/unread-count", description="Get unread count")
        
        # 13. Test Health Check
        print_colored("\n13. HEALTH CHECK ENDPOINTS", Colors.BLUE)
        
        self.test_endpoint("GET", "/health", description="Basic health check")
        self.test_endpoint("GET", "/ready", description="Readiness check")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print_colored("\n" + "="*60, Colors.BOLD)
        print_colored("TEST SUMMARY", Colors.BOLD)
        print_colored("="*60, Colors.BOLD)
        
        total = len(self.test_results)
        successful = sum(1 for r in self.test_results if r.get("success", False))
        failed = total - successful
        
        print(f"\nTotal tests: {total}")
        print_colored(f"Successful: {successful}", Colors.GREEN)
        print_colored(f"Failed: {failed}", Colors.RED if failed > 0 else Colors.GREEN)
        
        if failed > 0:
            print_colored("\nFailed endpoints:", Colors.RED)
            for result in self.test_results:
                if not result.get("success", False):
                    print(f"  - {result['method']} {result['endpoint']}")
                    if "error" in result:
                        print(f"    Error: {result['error']}")
                    elif "status_code" in result:
                        print(f"    Status: {result['status_code']} (Expected: {result.get('expected_status', 200)})")
        
        # Return exit code based on results
        return 0 if failed == 0 else 1

def main():
    """Main function"""
    # Wait for backend to be ready
    print_colored("Waiting for backend to be ready...", Colors.YELLOW)
    time.sleep(2)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print_colored("Backend is not responding correctly!", Colors.RED)
            return 1
    except requests.exceptions.ConnectionError:
        print_colored("Cannot connect to backend! Make sure it's running on port 5001.", Colors.RED)
        return 1
    
    # Run tests
    tester = APITester()
    return tester.run_tests()

if __name__ == "__main__":
    sys.exit(main())