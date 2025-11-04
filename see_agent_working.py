#!/usr/bin/env python3
"""
Interactive Agent Testing - See Your Job Search Agent in Action!

This script will help you:
1. Test your Railway deployment
2. Search for real jobs
3. See notifications in action
4. Monitor agent activity
"""

import httpx
import json
import asyncio
from datetime import datetime

def get_railway_url():
    """Help user find their Railway URL"""
    print("🔍 FINDING YOUR RAILWAY URL")
    print("=" * 40)
    print()
    print("Your Railway URL should look like one of these:")
    print("  • https://deploying-the-model-production.up.railway.app")
    print("  • https://web-production-xxxx.up.railway.app") 
    print("  • https://your-service-name.railway.app")
    print()
    print("📍 How to find it:")
    print("1. Go to railway.app and login")
    print("2. Click on your 'deploying_the-_model' project")
    print("3. Click on your service")
    print("4. Look for 'Domains' section - copy the URL")
    print()
    
    url = input("📝 Paste your Railway URL here: ").strip()
    if not url.startswith('http'):
        url = f"https://{url}"
    
    return url

async def test_agent_basics(url):
    """Test basic agent functionality"""
    print(f"\n🧪 TESTING AGENT AT: {url}")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Health Check
        print("\n1️⃣ Health Check...")
        try:
            response = await client.get(f"{url}/ping")
            if response.status_code == 200:
                print("   ✅ Agent is ALIVE and responding!")
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Cannot reach agent: {e}")
            return False

async def search_live_jobs(url):
    """Search for real jobs and see the agent work"""
    print(f"\n🔍 LIVE JOB SEARCH TEST")
    print("=" * 30)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Search for Data Engineering jobs
        search_payload = {
            "query": "data engineer python aws",
            "limit": 5,
            "resume_text": "Senior Data Engineer with 5+ years experience in Python, AWS, Spark, and machine learning pipelines",
            "enable_notifications": False  # Set to True if you have Twilio configured
        }
        
        print("🔍 Searching for: 'data engineer python aws'")
        print("👤 Resume: Senior Data Engineer profile")
        print("⏳ Searching... (this may take 10-30 seconds)")
        
        try:
            response = await client.post(
                f"{url}/api/search",
                json=search_payload,
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                
                print(f"\n✅ Found {len(jobs)} jobs!")
                print("=" * 40)
                
                for i, job in enumerate(jobs[:3], 1):  # Show top 3
                    print(f"\n📋 JOB #{i}:")
                    print(f"   Title: {job.get('title', 'No title')}")
                    print(f"   Company: {job.get('company', 'No company')}")
                    print(f"   Location: {job.get('location', 'Remote/Not specified')}")
                    print(f"   Score: {job.get('relevance_score', 'N/A')}/10")
                    
                    # Show a snippet of description
                    desc = job.get('description', '')
                    if desc:
                        snippet = desc[:150] + "..." if len(desc) > 150 else desc
                        print(f"   Description: {snippet}")
                    
                    print(f"   🔗 URL: {job.get('url', 'No URL')}")
                
                return len(jobs) > 0
            else:
                print(f"❌ Search failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Search error: {e}")
            return False

async def test_cover_letter(url, sample_job):
    """Test AI cover letter generation"""
    print(f"\n✍️ AI COVER LETTER GENERATION")
    print("=" * 35)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        cover_letter_payload = {
            "resume_text": "Senior Data Engineer with 5+ years experience building scalable data pipelines using Python, Apache Spark, AWS (S3, EMR, Redshift), and Kubernetes. Experienced in MLOps, CI/CD, and leading data platform migrations.",
            "job": sample_job
        }
        
        print(f"🎯 Generating cover letter for: {sample_job.get('title', 'Sample Job')}")
        print("⏳ Generating... (requires OpenAI API key)")
        
        try:
            response = await client.post(
                f"{url}/api/cover_letter",
                json=cover_letter_payload,
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                cover_letter = data.get('cover_letter', '')
                
                print(f"\n✅ Cover letter generated!")
                print("=" * 40)
                print(cover_letter[:500] + "..." if len(cover_letter) > 500 else cover_letter)
                return True
            else:
                print(f"❌ Cover letter generation failed: {response.status_code}")
                if response.status_code == 500:
                    print("   💡 This might mean OpenAI API key is not configured")
                return False
                
        except Exception as e:
            print(f"❌ Cover letter error: {e}")
            return False

async def monitor_agent_activity(url):
    """Show how to monitor ongoing agent activity"""
    print(f"\n📊 MONITORING AGENT ACTIVITY")
    print("=" * 35)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Check notification status
        print("📱 Notification System Status:")
        try:
            response = await client.get(f"{url}/api/notifications/status")
            if response.status_code == 200:
                data = response.json()
                print(f"   Configured: {data.get('configured', False)}")
                print(f"   Twilio: {data.get('twilio_configured', False)}")
                print(f"   Phone set: {data.get('phone_number_set', False)}")
                print(f"   SMS threshold: {data.get('sms_threshold', 'Not set')}")
            else:
                print("   ❌ Could not check notification status")
        except Exception as e:
            print(f"   ❌ Notification status error: {e}")
        
        # Check application tracking
        print("\n📋 Application Tracking:")
        try:
            response = await client.get(f"{url}/api/applications")
            if response.status_code == 200:
                data = response.json()
                apps = data.get('applications', [])
                print(f"   Tracked applications: {len(apps)}")
                
                if apps:
                    recent = apps[0]  # Most recent
                    print(f"   Latest: {recent.get('job_title', 'No title')} at {recent.get('company', 'No company')}")
            else:
                print("   ❌ Could not check applications")
        except Exception as e:
            print(f"   ❌ Application tracking error: {e}")

def show_continuous_monitoring_options(url):
    """Show options for continuous monitoring"""
    print(f"\n🔄 CONTINUOUS MONITORING OPTIONS")
    print("=" * 40)
    
    print("1️⃣ API Endpoints you can call regularly:")
    print(f"   • Job Search: POST {url}/api/search")
    print(f"   • Applications: GET {url}/api/applications")
    print(f"   • Status: GET {url}/api/notifications/status")
    
    print("\n2️⃣ Railway Logs (for debugging):")
    print("   • Go to Railway dashboard → your service → 'Logs' tab")
    print("   • See real-time application logs")
    
    print("\n3️⃣ Webhook Integration Ideas:")
    print("   • Set up cron jobs to call your API")
    print("   • Integration with Slack/Discord webhooks")
    print("   • Email alerts via services like SendGrid")
    
    print("\n4️⃣ Web Interface Option:")
    print("   • Deploy streamlit_app.py separately for web UI")
    print("   • Or build a simple React frontend")

async def main():
    """Main interactive testing flow"""
    print("🚀 JOB SEARCH AGENT - LIVE TESTING")
    print("=" * 45)
    print()
    print("This will help you see your agent working in real-time!")
    print()
    
    # Get Railway URL
    url = get_railway_url()
    
    # Test basic connectivity
    agent_alive = await test_agent_basics(url)
    if not agent_alive:
        print("\n❌ Cannot connect to agent. Please check your Railway URL.")
        return
    
    print("\n🎉 Great! Your agent is responding. Let's see it work...")
    
    # Test job search
    jobs_found = await search_live_jobs(url)
    
    if jobs_found:
        # Test cover letter generation
        sample_job = {
            "title": "Senior Data Engineer",
            "company": "TechCorp",
            "description": "We're looking for a Senior Data Engineer with expertise in Python, Apache Spark, and AWS to join our data platform team."
        }
        await test_cover_letter(url, sample_job)
    
    # Show monitoring capabilities
    await monitor_agent_activity(url)
    
    # Show continuous monitoring options
    show_continuous_monitoring_options(url)
    
    print(f"\n🎯 YOUR AGENT IS WORKING!")
    print("=" * 30)
    print("✅ Your job search agent is live and functional")
    print("📱 Configure environment variables for full features")
    print("🔄 Use the API endpoints for automation")
    print()
    print(f"🔗 Your live agent: {url}")

if __name__ == "__main__":
    asyncio.run(main())