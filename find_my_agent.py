"""
Quick Railway URL Finder and Tester
Based on your Railway project, let's find your public URL
"""

import httpx
import asyncio

# Common Railway URL patterns for your project
POSSIBLE_URLS = [
    "https://deploying-the-model-production.up.railway.app",
    "https://web-production-9cc62ab7.up.railway.app", 
    "https://service-production-18448b48.up.railway.app",
    "https://deploying-the-model-production-18448b48.up.railway.app",
    "https://deploying-the-model.up.railway.app",
    "https://deploying-the-model-9cc62ab7.up.railway.app"
]

async def find_working_url():
    """Try common URL patterns to find your working agent"""
    
    print("🔍 SEARCHING FOR YOUR DEPLOYED AGENT...")
    print("=" * 45)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        for url in POSSIBLE_URLS:
            print(f"Testing: {url}")
            try:
                response = await client.get(f"{url}/ping")
                if response.status_code == 200 and response.text.strip() == '"pong"':
                    print(f"✅ FOUND IT! Your agent is at: {url}")
                    return url
                else:
                    print(f"   ❌ No response")
            except Exception:
                print(f"   ❌ Not reachable")
        
        print("\n❌ Could not find agent with common patterns")
        return None

async def test_found_agent(url):
    """Test the agent functionality"""
    
    print(f"\n🧪 TESTING YOUR AGENT AT: {url}")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test basic info
        try:
            response = await client.get(f"{url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Agent Info: {data.get('message', 'Job Search Agent API')}")
            else:
                print(f"❌ Info endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Info test error: {e}")
        
        # Test job search
        print("\n🔍 Testing job search...")
        try:
            response = await client.get(f"{url}/api/search/priority?limit=2")
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                print(f"✅ Found {len(jobs)} priority jobs!")
                
                if jobs:
                    job = jobs[0]
                    print(f"   Sample: {job.get('title', 'No title')} at {job.get('company', 'No company')}")
            else:
                print(f"❌ Job search failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Job search error: {e}")
        
        # Test applications
        print("\n📋 Testing application tracking...")
        try:
            response = await client.get(f"{url}/api/applications")
            if response.status_code == 200:
                data = response.json()
                apps = data.get('applications', [])
                print(f"✅ Application tracker working! ({len(apps)} tracked)")
            else:
                print(f"❌ Application tracking failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Application tracking error: {e}")

async def main():
    print("🚀 RAILWAY AGENT FINDER")
    print("Based on your Railway project URL...")
    print()
    
    # Try to find the working URL
    working_url = await find_working_url()
    
    if working_url:
        await test_found_agent(working_url)
        
        print(f"\n🎉 SUCCESS! Your agent is working!")
        print("=" * 40)
        print(f"🔗 Your Agent URL: {working_url}")
        print()
        print("📋 What you can do now:")
        print(f"   • Visit: {working_url} (in browser)")
        print(f"   • Health: {working_url}/ping")
        print(f"   • Search Jobs: {working_url}/api/search/priority?limit=5")
        print(f"   • Applications: {working_url}/api/applications")
        print()
        print("🔧 To enable AI features:")
        print("   • Add OPENAI_API_KEY in Railway dashboard")
        print("   • Go to: Variables tab in your Railway project")
        
    else:
        print("\n📍 MANUAL STEPS TO FIND YOUR URL:")
        print("=" * 40)
        print("1. Go to https://railway.app")
        print("2. Click on your 'deploying_the-_model' project")
        print("3. Click on your service")
        print("4. Look for 'Domains' or 'Networking' tab")
        print("5. Copy the public URL (should end with .railway.app)")
        print("6. Test it by visiting: YOUR_URL/ping")

if __name__ == "__main__":
    asyncio.run(main())