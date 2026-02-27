"""
Diagnostic script to test authentication and summarization
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_flow():
    print("=" * 60)
    print("TESTING AUTHENTICATION & SUMMARIZATION FLOW")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # Test 2: Register User
    print("\n2. Testing Registration...")
    test_user = {
        "username": "testuser123",
        "email": "test123@test.com",
        "password": "Test1234",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 201:
            token = data.get('token')
            print(f"   ✓ Token received: {token[:50]}...")
        elif response.status_code == 400 and "already exists" in data.get('error', ''):
            print("   User already exists, trying login...")
            
            # Login instead
            login_data = {
                "username": test_user["username"],
                "password": test_user["password"]
            }
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            data = response.json()
            token = data.get('token')
            print(f"   ✓ Logged in, token: {token[:50]}...")
        else:
            print(f"   ERROR: {data}")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # Test 3: Verify Token
    print("\n3. Testing Token Verification...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 4: Summarize Text (The Issue!)
    print("\n4. Testing Summarization...")
    test_text = """
    Artificial intelligence is transforming the way we live and work. 
    Machine learning algorithms can now recognize patterns in data, make predictions, 
    and even create art. Natural language processing enables computers to understand 
    and generate human language, powering applications like chatbots, translation services, 
    and text summarization tools. Computer vision allows machines to interpret visual 
    information from the world around them. As AI continues to advance, it raises 
    important questions about ethics, privacy, and the future of work. Researchers 
    and policymakers are working to ensure that AI development benefits society while 
    minimizing potential risks.
    """
    
    summarize_data = {
        "text": test_text,
        "method": "extractive",  # Use extractive for faster testing
        "max_length": 100,
        "min_length": 50,
        "target_lang": "auto",
        "multilingual_mode": "translate"
    }
    
    try:
        print("   Sending request to /api/summarize...")
        response = requests.post(
            f"{BASE_URL}/summarize",
            json=summarize_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ SUCCESS!")
            print(f"   Summary: {data.get('summary', 'N/A')[:100]}...")
            print(f"   Original Length: {data.get('original_length')}")
            print(f"   Summary Length: {data.get('summary_length')}")
        else:
            print(f"   ERROR Response: {response.text}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        print(traceback.format_exc())
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_flow()