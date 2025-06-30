#!/usr/bin/env python3
"""
Quick demonstration of where outreach messages are saved in the LinkedIn Sourcing Agent
"""

import requests
import pandas as pd
import json
from datetime import datetime

print("🎯 LinkedIn Sourcing Agent - Outreach Message Storage Demo")
print("=" * 65)

# Test API to generate candidates with outreach messages
print("\n1️⃣ Generating candidates with outreach messages via API...")
response = requests.post("http://localhost:8000/source-candidates", json={
    "query": "Python Developer",
    "location": "San Francisco", 
    "limit": 2,
    "job_description": "We need a Python developer with Flask/Django experience for our fintech startup.",
    "export_excel": True
})

if response.status_code == 200:
    data = response.json()
    print(f"✅ Generated {data['candidates_found']} candidates")
    
    # Show message in API response
    print(f"\n2️⃣ Outreach message in API response:")
    candidate = data['top_candidates'][0]
    message = candidate.get('outreach_message', 'No message found')
    print(f"   Candidate: {candidate['name']}")
    print(f"   Message Preview: '{message[:80]}...'")
    
    # Find the latest Excel file
    import os
    excel_dir = "outputs/excel_exports"
    excel_files = [f for f in os.listdir(excel_dir) if f.endswith('.xlsx') and not f.startswith('~$')]
    if excel_files:
        latest_file = max(excel_files, key=lambda f: os.path.getmtime(os.path.join(excel_dir, f)))
        excel_path = os.path.join(excel_dir, latest_file)
        
        print(f"\n3️⃣ Checking Excel file: {latest_file}")
        
        try:
            # Check if Generated_Messages sheet exists and has content
            df = pd.read_excel(excel_path, sheet_name='Generated_Messages')
            
            if not df.empty and not df['Message_Content'].isna().all():
                print("✅ Outreach messages found in Excel:")
                for idx, row in df.iterrows():
                    if pd.notna(row['Message_Content']) and row['Message_Content'] != 'No outreach message available':
                        print(f"   📧 {row['Name']}: '{row['Message_Content'][:60]}...'")
                        print(f"      Type: {row['Message_Type']}, Length: {row['Character_Count']} chars")
                        break
            else:
                print("⚠️  No outreach messages found in Excel Generated_Messages sheet")
                print("   This might be because:")
                print("   - CLI was used instead of API")
                print("   - Messages weren't generated due to missing API keys")
                
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
    
    print(f"\n🎯 SUMMARY - Outreach Messages Are Saved In:")
    print(f"   📊 Excel Files: outputs/excel_exports/*.xlsx → 'Generated_Messages' sheet")
    print(f"   📱 API Response: JSON field 'outreach_message' for each candidate")
    print(f"   📝 JSON Files: outputs/json_data/*.json (API calls only)")
    
else:
    print(f"❌ API Error: {response.status_code}")
    print("Make sure the API server is running: python api_server.py")

print(f"\n💡 Pro Tip: Use the API (/source-candidates) for outreach generation!")
print(f"   CLI searches don't generate outreach messages (they're for quick candidate discovery)")
