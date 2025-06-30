"""
API Test Script for LinkedIn Sourcing Agent
Demonstrates all API endpoints and functionality
"""

import json
import requests
import time

API_BASE = "http://localhost:8000"

def test_basic_health():
    """Test basic API health"""
    print("🔍 Testing API Health...")
    
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        health_response = requests.get(f"{API_BASE}/health")
        print(f"✅ Health endpoint: {health_response.status_code}")
        health_data = health_response.json()
        print(f"   Status: {health_data['status']}")
        print(f"   Agent initialized: {health_data['agent_initialized']}")
        print(f"   Outreach generator: {health_data['outreach_generator_initialized']}")
        
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_demo_endpoint():
    """Test the demo endpoint with sample data"""
    print("\n🚀 Testing Demo Endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/demo")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Demo endpoint: {response.status_code}")
            print(f"   Job ID: {data['job_id']}")
            print(f"   Candidates found: {data['candidates_found']}")
            print(f"   Processing time: {data['processing_time_seconds']}s")
            print(f"   Top candidates: {len(data['top_candidates'])}")
            
            # Show first candidate details
            if data['top_candidates']:
                first_candidate = data['top_candidates'][0]
                print(f"\n📋 Sample Candidate:")
                print(f"   Name: {first_candidate['name']}")
                print(f"   Headline: {first_candidate['headline'][:80]}...")
                print(f"   Fit Score: {first_candidate['fit_score']}")
                print(f"   Key Characteristics: {first_candidate['key_characteristics']}")
                
                if first_candidate.get('outreach_message'):
                    print(f"   Outreach Message: {first_candidate['outreach_message'][:100]}...")
            
            return True
        else:
            print(f"❌ Demo failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Demo test failed: {e}")
        return False

def test_main_endpoint():
    """Test the main source-candidates endpoint"""
    print("\n🎯 Testing Main Sourcing Endpoint...")
    
    # Windsurf ML Research job (from hackathon)
    job_request = {
        "job_description": """
        Software Engineer, ML Research at Windsurf (Codeium)
        
        We're looking for a talented Software Engineer to join our ML Research team at Windsurf, 
        the company behind Codeium. You'll be working on training and optimizing Large Language Models 
        for code generation and AI-powered developer tools.
        
        Requirements:
        - Strong experience with Python, PyTorch, TensorFlow
        - Machine Learning and Deep Learning expertise
        - Experience with LLMs and code generation
        - Located in Mountain View, CA or remote
        
        Compensation: $140-300k + equity
        """,
        "location": "Mountain View",
        "max_candidates": 5,
        "include_outreach": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/source-candidates",
            json=job_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Main endpoint: {response.status_code}")
            print(f"   Job ID: {data['job_id']}")
            print(f"   Candidates found: {data['candidates_found']}")
            print(f"   Processing time: {data['processing_time_seconds']}s")
            print(f"   Search query used: {data['search_query_used']}")
            print(f"   Top candidates returned: {len(data['top_candidates'])}")
            
            # Show detailed candidate information
            for i, candidate in enumerate(data['top_candidates'][:2], 1):
                print(f"\n🏆 Top Candidate #{i}:")
                print(f"   Name: {candidate['name']}")
                print(f"   Headline: {candidate['headline']}")
                print(f"   Location: {candidate['location']}")
                print(f"   Fit Score: {candidate['fit_score']:.1f}/10")
                print(f"   Confidence: {candidate['confidence']}")
                
                print(f"   Score Breakdown:")
                for category, score in candidate['score_breakdown'].items():
                    print(f"     • {category.replace('_', ' ').title()}: {score:.1f}")
                
                print(f"   Key Characteristics:")
                for char in candidate['key_characteristics']:
                    print(f"     • {char}")
                
                print(f"   Job Match Reasons:")
                for reason in candidate['job_match_reasons']:
                    print(f"     • {reason}")
                
                if candidate.get('outreach_message'):
                    print(f"   Outreach Message:")
                    print(f"     {candidate['outreach_message'][:200]}...")
            
            return True
        else:
            print(f"❌ Main endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Main endpoint test failed: {e}")
        return False

def run_performance_test():
    """Quick performance test"""
    print("\n⚡ Performance Test...")
    
    start_time = time.time()
    response = requests.get(f"{API_BASE}/demo")
    end_time = time.time()
    
    if response.status_code == 200:
        processing_time = end_time - start_time
        data = response.json()
        agent_processing_time = data.get('processing_time_seconds', 0)
        
        print(f"✅ Performance Test Results:")
        print(f"   Total request time: {processing_time:.2f}s")
        print(f"   Agent processing time: {agent_processing_time:.2f}s")
        print(f"   Network overhead: {processing_time - agent_processing_time:.2f}s")
        print(f"   Candidates per second: {data['candidates_found'] / max(agent_processing_time, 0.01):.1f}")

def main():
    """Run all API tests"""
    print("🚀 LinkedIn Sourcing Agent API Test Suite")
    print("=" * 50)
    
    # Test 1: Basic health
    if not test_basic_health():
        print("❌ Basic health check failed. Is the server running?")
        return
    
    # Test 2: Demo endpoint
    if not test_demo_endpoint():
        print("❌ Demo endpoint failed")
        return
    
    # Test 3: Main endpoint
    if not test_main_endpoint():
        print("❌ Main endpoint failed")
        return
    
    # Test 4: Performance
    run_performance_test()
    
    print("\n🎉 All API tests passed!")
    print("\n📚 API Documentation available at: http://localhost:8000/docs")
    print("🔗 Interactive testing at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
