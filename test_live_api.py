#!/usr/bin/env python3
"""
Test script for the live Railway-deployed Job Search Agent API
"""

import httpx
import json
import asyncio

# Replace with your actual Railway URL
RAILWAY_URL = "https://your-app-name.up.railway.app"  # Update this!

async def test_live_api():
    """Test the live API endpoints"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🚀 Testing Live Job Search Agent API")
        print("=" * 50)
        
        # Test 1: Health Check
        print("1️⃣ Testing health check...")
        try:
            response = await client.get(f"{RAILWAY_URL}/ping")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            print("   ✅ Health check passed!" if response.status_code == 200 else "   ❌ Health check failed!")
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
        
        print()
        
        # Test 2: Root endpoint
        print("2️⃣ Testing root endpoint...")
        try:
            response = await client.get(f"{RAILWAY_URL}/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Message: {data.get('message', 'No message')}")
                print("   ✅ Root endpoint working!")
            else:
                print("   ❌ Root endpoint failed!")
        except Exception as e:
            print(f"   ❌ Root endpoint error: {e}")
        
        print()
        
        # Test 3: Job Search (priority endpoint - no auth needed)
        print("3️⃣ Testing job search...")
        try:
            response = await client.get(f"{RAILWAY_URL}/api/search/priority?limit=3")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                job_count = len(data.get('jobs', []))
                total_found = data.get('total_found', 0)
                print(f"   Jobs found: {job_count} (priority jobs)")
                print(f"   Total jobs searched: {total_found}")
                
                if job_count > 0:
                    first_job = data['jobs'][0]
                    print(f"   Sample job: {first_job.get('title', 'No title')} at {first_job.get('company', 'No company')}")
                print("   ✅ Job search working!")
            else:
                print("   ❌ Job search failed!")
        except Exception as e:
            print(f"   ❌ Job search error: {e}")
        
        print()
        
        # Test 4: Application tracking
        print("4️⃣ Testing application tracking...")
        try:
            response = await client.get(f"{RAILWAY_URL}/api/applications")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                app_count = len(data.get('applications', []))
                print(f"   Tracked applications: {app_count}")
                print("   ✅ Application tracking working!")
            else:
                print("   ❌ Application tracking failed!")
        except Exception as e:
            print(f"   ❌ Application tracking error: {e}")
        
        print()
        
        # Test 5: Notification status
        print("5️⃣ Testing notification system...")
        try:
            response = await client.get(f"{RAILWAY_URL}/api/notifications/status")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                configured = data.get('configured', False)
                twilio_configured = data.get('twilio_configured', False)
                phone_set = data.get('phone_number_set', False)
                
                print(f"   Notification system configured: {configured}")
                print(f"   Twilio configured: {twilio_configured}")
                print(f"   Phone number set: {phone_set}")
                print(f"   SMS threshold: {data.get('sms_threshold', 'Not set')}")
                print(f"   Call threshold: {data.get('call_threshold', 'Not set')}")
                print("   ✅ Notification status working!")
            else:
                print("   ❌ Notification status failed!")
        except Exception as e:
            print(f"   ❌ Notification status error: {e}")
        
        print()
        print("🎯 API Testing Complete!")
        print("=" * 50)


if __name__ == "__main__":
    print("📝 INSTRUCTIONS:")
    print("1. Update RAILWAY_URL in this script with your actual Railway deployment URL")
    print("2. Run: python test_live_api.py")
    print()
    
    # Check if URL is updated
    if "your-app-name" in RAILWAY_URL:
        print("❌ Please update RAILWAY_URL with your actual Railway deployment URL first!")
        print("   It should look like: https://deploying-the-model-production.up.railway.app")
    else:
        asyncio.run(test_live_api())