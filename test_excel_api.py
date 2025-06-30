#!/usr/bin/env python3
"""
Test script to verify Excel export functionality via API
"""

import requests
import json
import time
import os
import pandas as pd
from datetime import datetime

# API endpoint
BASE_URL = "http://localhost:8000"

def test_excel_export():
    """Test Excel export with company name and LinkedIn URL fixes"""
    
    print("🧪 Testing Excel Export API...")
    
    # Test request
    payload = {
        "query": "Frontend Developer",
        "location": "New York",
        "limit": 3,
        "job_description": "Looking for frontend developers with React experience",
        "export_excel": True
    }
    
    print(f"📤 Sending request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/source-candidates", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Job ID: {result['job_id']}")
            print(f"📊 Found {result['candidates_found']} candidates")
            
            # Find the most recent Excel file
            excel_dir = "outputs/excel_exports"
            excel_files = [f for f in os.listdir(excel_dir) if f.endswith('.xlsx') and not f.startswith('~$')]
            latest_file = max(excel_files, key=lambda f: os.path.getmtime(os.path.join(excel_dir, f)))
            
            print(f"📁 Latest Excel file: {latest_file}")
            
            # Read and verify the Excel file
            excel_path = os.path.join(excel_dir, latest_file)
            df = pd.read_excel(excel_path, sheet_name='Candidates')
            
            print("\n🔍 Verifying Excel Content:")
            print("=" * 60)
            print(df[['Name', 'Company', 'LinkedIn_URL']].to_string(index=False))
            print("=" * 60)
            
            # Check if companies are clean (no technical expertise)
            for index, row in df.iterrows():
                company = row['Company']
                if '•' in company or '|' in company:
                    print(f"⚠️  Warning: Company '{company}' still contains technical details")
                else:
                    print(f"✅ Clean company name: '{company}'")
            
            # Check LinkedIn URLs
            for index, row in df.iterrows():
                linkedin_url = row['LinkedIn_URL']
                if linkedin_url and 'linkedin.com' in linkedin_url:
                    print(f"✅ LinkedIn URL present: {row['Name']}")
                else:
                    print(f"❌ Missing LinkedIn URL: {row['Name']}")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_excel_export()
