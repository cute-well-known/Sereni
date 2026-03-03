import requests
import sys
import json
from datetime import datetime
import uuid

class SereniAPITester:
    def __init__(self, base_url="https://mindful-chat-49.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            result = {
                "test_name": name,
                "method": method,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success
            }
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                result["response_data"] = response.json() if response.content else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    result["error_response"] = response.json()
                    print(f"   Error: {result['error_response']}")
                except:
                    result["error_response"] = response.text
                    print(f"   Error: {response.text}")

            self.test_results.append(result)
            return success, response.json() if response.content and response.headers.get('content-type', '').startswith('application/json') else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                "test_name": name,
                "method": method,
                "endpoint": endpoint,
                "success": False,
                "error": str(e)
            }
            self.test_results.append(result)
            return False, {}

    def test_health_check(self):
        """Test health check endpoints"""
        print("\n=== HEALTH CHECK TESTS ===")
        self.run_test("Root endpoint", "GET", "", 200)
        self.run_test("Health check", "GET", "health", 200)
        
    def test_user_registration(self, name, email, password):
        """Test user registration"""
        print("\n=== USER REGISTRATION TEST ===")
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={"name": name, "email": email, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            print(f"   Registered user: {self.user_data['name']} ({self.user_data['email']})")
            return True
        return False

    def test_user_login(self, email, password):
        """Test user login"""
        print("\n=== USER LOGIN TEST ===")
        # Clear token first
        self.token = None
        success, response = self.run_test(
            "User Login",
            "POST", 
            "auth/login",
            200,
            data={"email": email, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            print(f"   Logged in user: {self.user_data['name']} ({self.user_data['email']})")
            return True
        return False

    def test_auth_me(self):
        """Test get current user"""
        print("\n=== GET CURRENT USER TEST ===")
        success, response = self.run_test(
            "Get current user",
            "GET",
            "auth/me", 
            200
        )
        if success:
            print(f"   Current user: {response.get('name')} ({response.get('email')})")
        return success

    def test_send_message(self, content, conversation_id=None):
        """Test sending a chat message"""
        print(f"\n=== SEND MESSAGE TEST ===")
        data = {"content": content}
        if conversation_id:
            data["conversation_id"] = conversation_id
            
        success, response = self.run_test(
            f"Send message: '{content[:30]}...'",
            "POST",
            "chat",
            200,
            data=data
        )
        
        if success:
            print(f"   Conversation ID: {response.get('conversation_id')}")
            print(f"   User message risk: {response.get('user_message', {}).get('risk_level')}")
            print(f"   AI response preview: {response.get('ai_message', {}).get('content', '')[:100]}...")
            return response.get('conversation_id'), response
        return None, {}

    def test_get_conversations(self):
        """Test getting conversation list"""
        print("\n=== GET CONVERSATIONS TEST ===")
        success, response = self.run_test(
            "Get conversations",
            "GET",
            "conversations",
            200
        )
        if success:
            print(f"   Found {len(response)} conversations")
            return response
        return []

    def test_get_conversation_messages(self, conversation_id):
        """Test getting messages from a conversation"""
        print(f"\n=== GET CONVERSATION MESSAGES TEST ===")
        success, response = self.run_test(
            "Get conversation messages",
            "GET",
            f"conversations/{conversation_id}/messages",
            200
        )
        if success:
            print(f"   Found {len(response)} messages in conversation")
            return response
        return []

    def test_delete_conversation(self, conversation_id):
        """Test deleting a conversation"""
        print(f"\n=== DELETE CONVERSATION TEST ===")
        success, response = self.run_test(
            "Delete conversation",
            "DELETE",
            f"conversations/{conversation_id}",
            200
        )
        return success

    def test_grounding_log(self):
        """Test grounding exercise logging"""
        print("\n=== GROUNDING LOG TEST ===")
        success, response = self.run_test(
            "Log grounding exercise",
            "POST",
            "grounding/log",
            200,
            data={"completed": True}
        )
        if success:
            print(f"   Grounding log ID: {response.get('id')}")
        return success

    def test_sentiment_analysis(self):
        """Test different sentiment analysis scenarios"""
        print("\n=== SENTIMENT ANALYSIS TESTS ===")
        
        # Test high-risk message
        conv_id, response = self.test_send_message("I want to kill myself")
        if response:
            risk_level = response.get('user_message', {}).get('risk_level')
            if risk_level == 'high':
                print("✅ High-risk detection working correctly")
            else:
                print(f"❌ Expected 'high' risk, got '{risk_level}'")
        
        # Test moderate distress message
        conv_id2, response2 = self.test_send_message("I feel hopeless and worthless, nobody cares about me")
        if response2:
            risk_level = response2.get('user_message', {}).get('risk_level')
            print(f"   Distress message risk level: {risk_level}")
            
        # Test normal message
        conv_id3, response3 = self.test_send_message("Hello, how are you today?")
        if response3:
            risk_level = response3.get('user_message', {}).get('risk_level')
            print(f"   Normal message risk level: {risk_level}")
            
        return [conv_id, conv_id2, conv_id3]

    def test_auth_protection(self):
        """Test protected endpoints without token"""
        print("\n=== AUTH PROTECTION TESTS ===")
        original_token = self.token
        self.token = None
        
        # Test protected endpoints should return 401
        success, _ = self.run_test("Protected endpoint without token", "GET", "auth/me", 401)
        if success:
            print("✅ Auth protection working correctly")
        else:
            print("❌ Auth protection failed - endpoint accessible without token")
            
        # Restore token
        self.token = original_token

    def run_full_test_suite(self):
        """Run complete test suite"""
        print("🚀 Starting Sereni API Test Suite")
        print(f"   Base URL: {self.base_url}")
        print("="*60)
        
        # Test health check
        self.test_health_check()
        
        # Generate unique test user
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"test_user_{timestamp}@example.com"
        test_password = "TestPass123!"
        test_name = f"Test User {timestamp}"
        
        # Test registration
        if not self.test_user_registration(test_name, test_email, test_password):
            print("❌ Registration failed, stopping tests")
            return self.get_summary()
            
        # Test auth/me
        self.test_auth_me()
        
        # Test chat functionality and sentiment analysis
        conversation_ids = self.test_sentiment_analysis()
        
        # Test conversation management
        conversations = self.test_get_conversations()
        if conversations and len(conversations) > 0:
            # Test getting messages from first conversation
            first_conv_id = conversations[0]['id']
            self.test_get_conversation_messages(first_conv_id)
            
        # Test grounding log
        self.test_grounding_log()
        
        # Test login with same user
        if not self.test_user_login(test_email, test_password):
            print("❌ Login test failed")
            
        # Test auth protection
        self.test_auth_protection()
        
        # Clean up - delete test conversations
        if conversation_ids:
            for conv_id in conversation_ids:
                if conv_id:
                    self.test_delete_conversation(conv_id)
        
        return self.get_summary()

    def get_summary(self):
        """Get test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "No tests run")
        
        # Show failed tests
        failed_tests = [t for t in self.test_results if not t.get('success', False)]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   - {test['test_name']}: {test.get('error', 'Status code mismatch')}")
                
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0,
            "test_results": self.test_results
        }

def main():
    tester = SereniAPITester()
    summary = tester.run_full_test_suite()
    
    # Return appropriate exit code
    return 0 if summary["failed_tests"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())