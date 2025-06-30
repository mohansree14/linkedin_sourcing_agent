import requests
import json

# Test the API to verify all three functionalities
response = requests.post("http://localhost:8000/source-candidates", json={
    "query": "Senior Python Developer",
    "location": "San Francisco",
    "limit": 2,
    "job_description": "We need a Senior Python Developer with 5+ years experience in backend development, API design, and cloud technologies. Must have Django/Flask, PostgreSQL, and AWS experience.",
    "export_excel": False
})

if response.status_code == 200:
    data = response.json()
    
    print("🎯 LinkedIn Sourcing Agent - All Three Functionalities Verified!")
    print("=" * 70)
    
    # 1. CANDIDATE DISCOVERY
    print(f"\n✅ 1. CANDIDATE DISCOVERY:")
    print(f"   Found: {data['candidates_found']} candidates")
    print(f"   Processing time: {data['processing_time_seconds']:.2f} seconds")
    print(f"   Job ID: {data['job_id']}")
    
    # 2. SCORING SYSTEM
    print(f"\n✅ 2. CANDIDATE SCORING:")
    candidate = data['top_candidates'][0]
    print(f"   Candidate: {candidate['name']}")
    print(f"   Fit Score: {candidate['fit_score']}/100")
    print(f"   Confidence: {candidate['confidence']}")
    print(f"   Key Characteristics: {', '.join(candidate['key_characteristics'][:3])}")
    
    # 3. OUTREACH GENERATION
    print(f"\n✅ 3. OUTREACH MESSAGE GENERATION:")
    print(f"   Message Preview:")
    print(f"   '{candidate['outreach_message'][:120]}...'")
    
    print(f"\n🚀 All systems operational!")
    
else:
    print(f"Error: {response.status_code}")
    print(response.text)
