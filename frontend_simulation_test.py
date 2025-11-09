#!/usr/bin/env python3
"""
Frontend Simulation Test - Simulate exact frontend behavior
Tests the exact same requests that the frontend would make
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - using exact same URL as frontend
BASE_URL = "https://plannapp.preview.emergentagent.com/api"
TEST_USER_EMAIL = "testadmin@example.com"
TEST_USER_PASSWORD = "testpass123"

class FrontendSimulator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def simulate_login(self):
        """Simulate frontend login process"""
        print("🔐 Simulating frontend login...")
        
        try:
            # Frontend uses form data for login (OAuth2PasswordRequestForm)
            payload = {
                "username": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/token", data=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                self.auth_token = response_data.get("access_token")
                print(f"✅ Login successful, token obtained: {self.auth_token[:20]}...")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login exception: {str(e)}")
            return False
    
    def simulate_staff_add_request(self):
        """Simulate exact frontend staff add request"""
        print("\n👤 Simulating frontend staff add request...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        # Exact payload that frontend sends
        payload = {
            "username": "newfrontendstaff@example.com",
            "password": "staffpass123",
            "full_name": "New Frontend Staff"
        }
        
        # Exact headers that frontend sends
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"📤 Sending request to: {BASE_URL}/staff/add")
            print(f"📤 Headers: {headers}")
            print(f"📤 Payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(
                f"{BASE_URL}/staff/add", 
                json=payload,
                headers=headers
            )
            
            print(f"📥 Response Status: {response.status_code}")
            print(f"📥 Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"📥 Response Body: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📥 Response Body (raw): {response.text}")
            
            if response.status_code == 200:
                print("✅ Staff add request successful!")
                return True
            elif response.status_code == 422:
                print("❌ 422 Validation Error - This is the issue!")
                return False
            elif response.status_code == 400:
                print("⚠️ 400 Bad Request - User might already exist")
                return True  # This is expected if user exists
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Request exception: {str(e)}")
            return False
    
    def test_authentication_validity(self):
        """Test if the token is valid by calling /users endpoint"""
        print("\n🔍 Testing authentication validity...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        try:
            response = self.session.get(f"{BASE_URL}/users", headers=headers)
            
            if response.status_code == 200:
                users = response.json()
                print(f"✅ Authentication valid, found {len(users)} users")
                return True
            elif response.status_code == 401:
                print("❌ Authentication invalid - token expired or invalid")
                return False
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication test exception: {str(e)}")
            return False
    
    def test_different_payloads(self):
        """Test different payload formats to identify validation issues"""
        print("\n🧪 Testing different payload formats...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        test_payloads = [
            {
                "name": "Valid payload",
                "data": {
                    "username": "test1@example.com",
                    "password": "pass123",
                    "full_name": "Test User 1"
                }
            },
            {
                "name": "Empty strings",
                "data": {
                    "username": "",
                    "password": "",
                    "full_name": ""
                }
            },
            {
                "name": "Missing full_name",
                "data": {
                    "username": "test2@example.com",
                    "password": "pass123"
                }
            },
            {
                "name": "Extra fields",
                "data": {
                    "username": "test3@example.com",
                    "password": "pass123",
                    "full_name": "Test User 3",
                    "extra_field": "should be ignored"
                }
            }
        ]
        
        for test_case in test_payloads:
            print(f"\n🔬 Testing: {test_case['name']}")
            try:
                response = self.session.post(
                    f"{BASE_URL}/staff/add",
                    json=test_case['data'],
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        print(f"   Error: {json.dumps(error_data, indent=6)}")
                    except:
                        print(f"   Error (raw): {response.text}")
                else:
                    print("   ✅ Success")
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
    
    def run_simulation(self):
        """Run complete frontend simulation"""
        print("🚀 Starting Frontend Simulation Test")
        print("=" * 60)
        
        # Step 1: Login
        if not self.simulate_login():
            print("❌ Cannot proceed without login")
            return False
        
        # Step 2: Test authentication
        if not self.test_authentication_validity():
            print("❌ Authentication is invalid")
            return False
        
        # Step 3: Test staff add (main issue)
        success = self.simulate_staff_add_request()
        
        # Step 4: Test different payloads
        self.test_different_payloads()
        
        print("\n" + "=" * 60)
        print("📊 SIMULATION COMPLETE")
        print("=" * 60)
        
        return success

if __name__ == "__main__":
    simulator = FrontendSimulator()
    success = simulator.run_simulation()
    sys.exit(0 if success else 1)