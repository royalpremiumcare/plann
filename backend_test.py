#!/usr/bin/env python3
"""
Backend API Testing for PLANN Appointment Scheduling App
Tests core endpoints as requested by user
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://plannapp.preview.emergentagent.com/api"
TEST_USER_EMAIL = "test@test.com"
TEST_USER_PASSWORD = "test123"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def test_register_user(self):
        """Test user registration"""
        try:
            payload = {
                "username": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_FULL_NAME,
                "organization_name": TEST_ORG_NAME
            }
            
            response = self.session.post(f"{BASE_URL}/register", json=payload)
            
            if response.status_code == 200:
                self.log_test("User Registration", True, "Successfully registered new user")
                return True
            elif response.status_code == 400:
                # User might already exist
                response_data = response.json()
                if "already registered" in response_data.get("detail", ""):
                    self.log_test("User Registration", True, "User already exists (expected)")
                    return True
                else:
                    self.log_test("User Registration", False, f"Registration failed: {response_data.get('detail')}", response_data)
                    return False
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_login(self):
        """Test user login and get JWT token"""
        try:
            # Using OAuth2PasswordRequestForm format
            payload = {
                "username": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/token", data=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                self.auth_token = response_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("User Login", True, "Successfully obtained JWT token")
                return True
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False
    
    def test_get_users(self):
        """Test GET /api/users endpoint to verify authentication"""
        try:
            response = self.session.get(f"{BASE_URL}/users")
            
            if response.status_code == 200:
                users = response.json()
                self.log_test("Get Users", True, f"Retrieved {len(users)} users")
                return True
            elif response.status_code == 401:
                self.log_test("Get Users", False, "Authentication failed - invalid token", response.json())
                return False
            else:
                self.log_test("Get Users", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_test("Get Users", False, f"Exception: {str(e)}")
            return False
    
    def test_add_staff_valid_data(self):
        """Test POST /api/staff/add with valid data"""
        try:
            payload = {
                "username": TEST_STAFF_EMAIL,
                "password": TEST_STAFF_PASSWORD,
                "full_name": TEST_STAFF_FULL_NAME
            }
            
            response = self.session.post(f"{BASE_URL}/staff/add", json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                self.log_test("Add Staff - Valid Data", True, "Successfully added staff member", response_data)
                return True
            elif response.status_code == 422:
                response_data = response.json()
                self.log_test("Add Staff - Valid Data", False, f"422 Validation Error: {response_data}", response_data)
                return False
            elif response.status_code == 400:
                response_data = response.json()
                if "already registered" in response_data.get("detail", ""):
                    self.log_test("Add Staff - Valid Data", True, "Staff already exists (expected)")
                    return True
                else:
                    self.log_test("Add Staff - Valid Data", False, f"400 Error: {response_data.get('detail')}", response_data)
                    return False
            else:
                self.log_test("Add Staff - Valid Data", False, f"HTTP {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_test("Add Staff - Valid Data", False, f"Exception: {str(e)}")
            return False
    
    def test_add_staff_missing_fields(self):
        """Test POST /api/staff/add with missing required fields"""
        test_cases = [
            {"username": TEST_STAFF_EMAIL, "password": TEST_STAFF_PASSWORD},  # Missing full_name
            {"username": TEST_STAFF_EMAIL, "full_name": TEST_STAFF_FULL_NAME},  # Missing password
            {"password": TEST_STAFF_PASSWORD, "full_name": TEST_STAFF_FULL_NAME},  # Missing username
            {}  # Empty payload
        ]
        
        for i, payload in enumerate(test_cases):
            try:
                response = self.session.post(f"{BASE_URL}/staff/add", json=payload)
                
                if response.status_code == 422:
                    self.log_test(f"Add Staff - Missing Fields {i+1}", True, "Correctly returned 422 for missing fields")
                else:
                    self.log_test(f"Add Staff - Missing Fields {i+1}", False, f"Expected 422, got {response.status_code}", response.json())
                    
            except Exception as e:
                self.log_test(f"Add Staff - Missing Fields {i+1}", False, f"Exception: {str(e)}")
    
    def test_add_staff_invalid_data(self):
        """Test POST /api/staff/add with invalid data types"""
        test_cases = [
            {"username": 123, "password": TEST_STAFF_PASSWORD, "full_name": TEST_STAFF_FULL_NAME},  # Invalid username type
            {"username": TEST_STAFF_EMAIL, "password": 123, "full_name": TEST_STAFF_FULL_NAME},  # Invalid password type
            {"username": TEST_STAFF_EMAIL, "password": TEST_STAFF_PASSWORD, "full_name": 123},  # Invalid full_name type
        ]
        
        for i, payload in enumerate(test_cases):
            try:
                response = self.session.post(f"{BASE_URL}/staff/add", json=payload)
                
                if response.status_code == 422:
                    self.log_test(f"Add Staff - Invalid Data {i+1}", True, "Correctly returned 422 for invalid data types")
                else:
                    self.log_test(f"Add Staff - Invalid Data {i+1}", False, f"Expected 422, got {response.status_code}", response.json())
                    
            except Exception as e:
                self.log_test(f"Add Staff - Invalid Data {i+1}", False, f"Exception: {str(e)}")
    
    def test_add_staff_without_auth(self):
        """Test POST /api/staff/add without authentication"""
        try:
            # Temporarily remove auth header
            original_headers = self.session.headers.copy()
            if "Authorization" in self.session.headers:
                del self.session.headers["Authorization"]
            
            payload = {
                "username": "noauth@example.com",
                "password": "password123",
                "full_name": "No Auth User"
            }
            
            response = self.session.post(f"{BASE_URL}/staff/add", json=payload)
            
            # Restore headers
            self.session.headers = original_headers
            
            if response.status_code == 401:
                self.log_test("Add Staff - No Auth", True, "Correctly returned 401 for unauthenticated request")
                return True
            else:
                self.log_test("Add Staff - No Auth", False, f"Expected 401, got {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_test("Add Staff - No Auth", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Backend API Tests for Staff Management")
        print("=" * 60)
        
        # Test authentication flow
        if not self.test_register_user():
            print("❌ Registration failed, stopping tests")
            return False
            
        if not self.test_login():
            print("❌ Login failed, stopping tests")
            return False
            
        if not self.test_get_users():
            print("❌ Authentication verification failed, stopping tests")
            return False
        
        # Test staff management endpoints
        self.test_add_staff_valid_data()
        self.test_add_staff_missing_fields()
        self.test_add_staff_invalid_data()
        self.test_add_staff_without_auth()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)