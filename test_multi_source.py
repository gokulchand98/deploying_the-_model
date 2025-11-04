#!/usr/bin/env python3
"""Test script for multi-source job scraping."""

import asyncio
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_scrapers():
    """Test all job scrapers individually and combined."""
    print("🔍 Testing Multi-Source Job Scrapers...")
    print("=" * 50)
    
    try:
        from app.scrapers import DiceScraper, IndeedScraper, LinkedInScraper, search_jobs_multi_source
        
        query = "data engineer"
        location = "United States"
        limit = 3
        
        print(f"Query: {query}")
        print(f"Location: {location}")
        print(f"Limit per source: {limit}")
        print()
        
        # Test individual scrapers
        scrapers = [
            ("Dice", DiceScraper()),
            ("Indeed", IndeedScraper()),
            ("LinkedIn", LinkedInScraper())
        ]
        
        all_results = []
        
        for name, scraper in scrapers:
            print(f"🌐 Testing {name}...")
            try:
                jobs = await scraper.search_jobs(query, location, limit)
                print(f"   ✅ Found {len(jobs)} jobs from {name}")
                
                for i, job in enumerate(jobs[:2], 1):  # Show first 2
                    print(f"   {i}. {job.get('title', 'No title')} at {job.get('company', 'No company')}")
                    print(f"      URL: {job.get('url', 'No URL')[:80]}...")
                
                all_results.extend(jobs)
                
            except Exception as e:
                print(f"   ❌ {name} failed: {e}")
            
            print()
        
        # Test combined multi-source search
        print("🎯 Testing Multi-Source Combined Search...")
        try:
            combined_jobs = await search_jobs_multi_source(query, location, 10)
            print(f"   ✅ Combined search found {len(combined_jobs)} unique jobs")
            
            # Count by source
            source_counts = {}
            for job in combined_jobs:
                source = job.get('source', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            print("   📊 Jobs by source:")
            for source, count in source_counts.items():
                print(f"      {source}: {count} jobs")
            
            print("\n   🔗 Sample jobs:")
            for i, job in enumerate(combined_jobs[:5], 1):
                print(f"   {i}. [{job.get('source', 'Unknown')}] {job.get('title', 'No title')}")
                print(f"      Company: {job.get('company', 'No company')}")
                print(f"      Location: {job.get('location', 'No location')}")
                print(f"      URL: {job.get('url', 'No URL')}")
                print()
        
        except Exception as e:
            print(f"   ❌ Combined search failed: {e}")
        
        print("=" * 50)
        print("✅ Scraper testing complete!")
        
        return len(all_results) > 0
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return False


async def test_agent_integration():
    """Test the enhanced agent with multi-source search."""
    print("\n🤖 Testing Agent Integration...")
    print("=" * 50)
    
    try:
        from app.agent import search_jobs
        
        print("Testing enhanced search_jobs function...")
        jobs = await search_jobs("data engineer", limit=8)
        
        print(f"✅ Agent found {len(jobs)} jobs")
        
        # Count by source
        source_counts = {}
        for job in jobs:
            source = job.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print("📊 Jobs by source:")
        for source, count in source_counts.items():
            print(f"   {source}: {count} jobs")
        
        print("\n🎯 Sample results:")
        for i, job in enumerate(jobs[:3], 1):
            score = job.get('relevance_score', 0)
            print(f"{i}. [{job.get('source', '?')}] {job.get('title', 'No title')} (Score: {score})")
            print(f"   Company: {job.get('company', 'No company')}")
            print(f"   URL: {job.get('url', 'No URL')}")
            print()
        
        return len(jobs) > 0
        
    except Exception as e:
        print(f"❌ Agent integration failed: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Starting Multi-Source Job Search Tests\n")
        
        # Test scrapers
        scrapers_ok = await test_scrapers()
        
        # Test agent integration
        agent_ok = await test_agent_integration()
        
        if scrapers_ok and agent_ok:
            print("\n🎉 All tests passed! Multi-source job search is working.")
            return 0
        else:
            print("\n⚠️ Some tests failed. Check the output above.")
            return 1
    
    exit_code = asyncio.run(main())
    exit(exit_code)