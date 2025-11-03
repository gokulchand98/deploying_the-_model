#!/usr/bin/env python3
"""Quick test script to demonstrate the specialized job search agent functionality."""

import asyncio
import os
from app.agent import search_jobs, generate_cover_letter_sync, PRIORITY_KEYWORDS

async def test_search():
    print("🔍 Testing DE/MLOps/Cloud Job Search Agent")
    print("=" * 50)
    
    # Test priority keyword scoring
    print("📊 Priority Keywords:")
    for category, keywords in PRIORITY_KEYWORDS.items():
        print(f"  {category}: {', '.join(keywords[:3])}...")
    
    print("\n🎯 Searching for priority jobs...")
    try:
        jobs = await search_jobs("", limit=5)  # Use default priority search
        
        print(f"\n✅ Found {len(jobs)} jobs, sorted by relevance:")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job['title']} @ {job['company']}")
            print(f"   🏆 Relevance Score: {job.get('relevance_score', 0)}")
            print(f"   📍 Location: {job.get('location', 'Remote')}")
            
            # Test cover letter generation (without OpenAI for demo)
            sample_resume = "Senior Data Engineer with 5+ years experience in Apache Spark, AWS, Python, and ML pipelines."
            cover_letter = generate_cover_letter_sync(sample_resume, job)
            print(f"   📝 Cover Letter Preview: {cover_letter[:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: This requires internet connection to query the Remotive API")

if __name__ == "__main__":
    asyncio.run(test_search())