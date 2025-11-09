#!/usr/bin/env python3
"""
Detailed 422 Error Investigation
Investigate the exact conditions that cause 422 errors
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BASE_URL = "https://plannapp.preview.emergentagent.com/api"

class DetailedInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_counter = 0
        
    def get_auth_token(self):
        """Get a fresh auth token"""
        try:
            payload = {
                "username": "testadmin@example.com",
                "password": "testpass123"
            }
            
            response = self.session.post(f"{BASE_URL}/token", data=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                self.auth_token = response_data.get("access_token")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Login exception: {str(e)}")
            return False
    
    def test_staff_add_with_variations(self):
        """Test staff add with various conditions that might cause 422"""
        
        test_cases = [
            {
                "name": "Standard valid request",
                "payload": {
                    "username": f"test{self.test_counter}@example.com",
                    "password": "testpass123",
                    "full_name": "Test User"
                },
                "headers": {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Empty string values",
                "payload": {
                    "username": "",
                    "password": "",
                    "full_name": ""
                },
                "headers": {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "None values",
                "payload": {
                    "username": None,
                    "password": None,
                    "full_name": None
                },
                "headers": {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Missing fields",
                "payload": {
                    "username": f"test{self.test_counter+1}@example.com"
                },
                "headers": {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Wrong data types",
                "payload": {
                    "username": 123,
                    "password": 456,
                    "full_name": 789
                },
                "headers": {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Invalid email format",
                "payload": {
                    "username": "not-an-email",
                    "password": "testpass123",
                    "full_name": "Test User"
                },
                "headers": {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Very long strings",
                "payload": {
                    "username": "a" * 1000 + "@example.com",
                    "password": "b" * 1000,
                    "full_name": "c" * 1000
                },
                "headers": {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Special characters",
                "payload": {
                    "username": "test+special@example.com",
                    "password": "pass!@#$%^&*()",
                    "full_name": "Test Üser Çağlar Şahin"
                },
                "headers": {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Wrong Content-Type",
                "payload": {
                    "username": f"test{self.test_counter+2}@example.com",
                    "password": "testpass123",
                    "full_name": "Test User"
                },
                "headers": {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            },
            {
                "name": "No Content-Type",
                "payload": {
                    "username": f"test{self.test_counter+3}@example.com",
                    "password": "testpass123",
                    "full_name": "Test User"
                },
                "headers": {
                    "Authorization": f"Bearer {self.auth_token}"
                }
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases):
            self.test_counter += 1
            print(f"\n🧪 Test {i+1}: {test_case['name']}")
            
            try:
                # Update payload with current counter if needed
                if 'username' in test_case['payload'] and isinstance(test_case['payload']['username'], str):
                    if 'test{' in str(test_case['payload']['username']):
                        test_case['payload']['username'] = f"test{self.test_counter}@example.com"
                
                response = self.session.post(
                    f"{BASE_URL}/staff/add",
                    json=test_case['payload'],
                    headers=test_case['headers']
                )
                
                result = {
                    "test_name": test_case['name'],
                    "status_code": response.status_code,
                    "success": response.status_code in [200, 400],  # 400 is OK for duplicate users
                    "payload": test_case['payload'],
                    "headers": test_case['headers']
                }
                
                try:
                    result["response_data"] = response.json()
                except:
                    result["response_data"] = response.text
                
                results.append(result)
                
                if response.status_code == 422:
                    print(f"   ❌ 422 ERROR FOUND!")
                    print(f"   📤 Payload: {json.dumps(test_case['payload'], indent=6)}")
                    print(f"   📥 Response: {json.dumps(result['response_data'], indent=6)}")
                elif response.status_code == 200:
                    print(f"   ✅ Success")
                elif response.status_code == 400:
                    print(f"   ⚠️ 400 (expected for duplicates)")
                else:
                    print(f"   ❓ Status: {response.status_code}")
                
                # Small delay between requests
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                results.append({
                    "test_name": test_case['name'],
                    "status_code": "EXCEPTION",
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def test_concurrent_requests(self):
        """Test multiple concurrent requests to see if there are race conditions"""
        print("\n🔄 Testing concurrent requests...")
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def make_request(thread_id):
            try:
                payload = {
                    "username": f"concurrent{thread_id}@example.com",
                    "password": "testpass123",
                    "full_name": f"Concurrent User {thread_id}"
                }
                
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    f"{BASE_URL}/staff/add",
                    json=payload,
                    headers=headers
                )
                
                results_queue.put({
                    "thread_id": thread_id,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code != 422 else response.text
                })
                
            except Exception as e:
                results_queue.put({
                    "thread_id": thread_id,
                    "status_code": "EXCEPTION",
                    "error": str(e)
                })
        
        # Launch 5 concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        concurrent_results = []
        while not results_queue.empty():
            result = results_queue.get()
            concurrent_results.append(result)
            print(f"   Thread {result['thread_id']}: Status {result['status_code']}")
        
        return concurrent_results
    
    def run_investigation(self):
        """Run complete investigation"""
        print("🔍 Starting Detailed 422 Error Investigation")
        print("=" * 60)
        
        # Get auth token
        if not self.get_auth_token():
            print("❌ Cannot proceed without authentication")
            return False
        
        print(f"✅ Authentication successful")
        
        # Test various conditions
        variation_results = self.test_staff_add_with_variations()
        
        # Test concurrent requests
        concurrent_results = self.test_concurrent_requests()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(variation_results)
        error_422_tests = [r for r in variation_results if r.get('status_code') == 422]
        
        print(f"Total variation tests: {total_tests}")
        print(f"422 errors found: {len(error_422_tests)}")
        
        if error_422_tests:
            print("\n❌ CONDITIONS THAT CAUSE 422 ERRORS:")
            for result in error_422_tests:
                print(f"  - {result['test_name']}")
                if 'response_data' in result:
                    print(f"    Response: {result['response_data']}")
        else:
            print("\n✅ No 422 errors found in variation tests")
        
        concurrent_422s = [r for r in concurrent_results if r.get('status_code') == 422]
        if concurrent_422s:
            print(f"\n⚠️ Concurrent requests with 422 errors: {len(concurrent_422s)}")
        
        return len(error_422_tests) == 0 and len(concurrent_422s) == 0

if __name__ == "__main__":
    investigator = DetailedInvestigator()
    success = investigator.run_investigation()
    sys.exit(0 if success else 1)