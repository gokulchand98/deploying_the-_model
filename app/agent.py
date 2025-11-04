"""Agent logic: job search and cover letter generation.

Specialized for Data Engineering, MLOps, and Cloud Engineering roles.
- search_jobs(query): uses multiple sources (Remotive API + Dice + LinkedIn + Indeed)
- generate_cover_letter(resume_text, job): uses OpenAI ChatCompletion to generate tailored cover letters.

Focuses on high-priority job types: Data Engineering, MLOps, Cloud Engineering.
Multi-source job search for comprehensive coverage.
"""
from typing import List, Dict, Optional
import os
import httpx
import asyncio

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

REMOTIVE_SEARCH_URL = "https://remotive.com/api/remote-jobs"

# Priority job types and related keywords
PRIORITY_KEYWORDS = {
    "data_engineering": ["data engineer", "data engineering", "data pipeline", "etl", "apache spark", "kafka", "airflow", "databricks", "snowflake"],
    "mlops": ["mlops", "ml engineer", "machine learning engineer", "ml platform", "kubeflow", "mlflow", "sagemaker", "model deployment"],
    "cloud_engineering": ["cloud engineer", "devops engineer", "aws engineer", "azure engineer", "gcp engineer", "kubernetes", "terraform", "infrastructure"]
}


def _score_job_relevance(job_title: str, job_description: str) -> int:
    """Score job relevance based on priority keywords. Higher score = more relevant."""
    from .rubrics import rubrics
    
    # Create a temporary job dict for scoring
    job = {
        'title': job_title,
        'description': job_description,
        'company': '',
        'location': ''
    }
    
    # Use rubrics-based scoring
    score = rubrics.get_job_score(job)
    
    # Fallback to original scoring if rubrics score is too low
    if score < 3:
        title_lower = job_title.lower()
        desc_lower = job_description.lower()
        
        # High priority matches in title (worth more)
        for category, keywords in PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in title_lower:
                    score += 10
                elif keyword in desc_lower:
                    score += 3
    
    return score


async def search_jobs_remotive_only(query: str, limit: int = 10) -> List[Dict]:
    """Search jobs using only Remotive API (legacy function)."""
    # If no specific query, use our priority terms
    if not query or query.strip() == "":
        query = "data engineer OR mlops OR cloud engineer OR devops"
    
    params = {"search": query}
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(REMOTIVE_SEARCH_URL, params=params)
        r.raise_for_status()
        data = r.json()

    jobs = []
    for item in data.get("jobs", [])[:limit*3]:  # Get extra jobs to filter/sort (more because we're filtering by location)
        location = item.get("candidate_required_location", "").lower()
        
        # Filter for United States jobs only
        us_indicators = ["usa", "united states", "us", "america", "american", "remote us", "us remote", 
                        "remote usa", "usa remote", "remote (us)", "remote - us", "us only", "usa only"]
        
        if not any(indicator in location for indicator in us_indicators):
            continue  # Skip non-US jobs
        
        job = {
            "id": f"remotive_{item.get('id')}",
            "source": "Remotive",
            "title": item.get("title"),
            "company": item.get("company_name"),
            "location": item.get("candidate_required_location"),
            "url": item.get("url"),
            "description": item.get("description"),
        }
        # Add relevance score
        job["relevance_score"] = _score_job_relevance(job.get("title", ""), job.get("description", ""))
        jobs.append(job)
    
    # Sort by relevance score (highest first) and return top results
    jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return jobs[:limit]


async def search_jobs(query: str, limit: int = 10, resume_text: str = "", enable_notifications: bool = False) -> List[Dict]:
    """Enhanced job search using multiple sources: Remotive + Dice + LinkedIn + Indeed.

    Returns a comprehensive list of job opportunities from all major job sites.
    Prioritizes DE/MLOps/Cloud roles and filters for US jobs only.
    """
    try:
        # Import scrapers
        from .scrapers import search_jobs_multi_source
        
        # If no specific query, use our priority terms
        if not query or query.strip() == "":
            query = "data engineer OR mlops OR cloud engineer OR devops"
        
        # Search multiple sources concurrently
        scraper_limit = max(1, limit // 2)  # Half from scrapers, half from Remotive
        remotive_limit = limit - scraper_limit
        
        # Run both searches concurrently
        tasks = [
            search_jobs_remotive_only(query, remotive_limit),
            search_jobs_multi_source(query, "United States", scraper_limit)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_jobs = []
        
        # Process Remotive results
        if isinstance(results[0], list):
            all_jobs.extend(results[0])
        elif isinstance(results[0], Exception):
            print(f"Remotive search failed: {results[0]}")
        
        # Process scraper results
        if isinstance(results[1], list):
            scraped_jobs = results[1]
            
            # Add scoring and processing to scraped jobs
            for job in scraped_jobs:
                if not job.get("relevance_score"):
                    job["relevance_score"] = _score_job_relevance(
                        job.get("title", ""), 
                        job.get("description", "")
                    )
            
            all_jobs.extend(scraped_jobs)
        elif isinstance(results[1], Exception):
            print(f"Multi-source scraping failed: {results[1]}")
        
        # Remove duplicates based on title and company
        seen = set()
        unique_jobs = []
        
        for job in all_jobs:
            job_key = (job.get('title', '').lower().strip(), job.get('company', '').lower().strip())
            if job_key not in seen and job.get('title') and job.get('company'):
                seen.add(job_key)
                
                # Add resume matching and notifications
                if resume_text:
                    try:
                        from .notifications import calculate_resume_match_score, notifications
                        job["resume_match_score"] = calculate_resume_match_score(job, resume_text)
                        
                        # Send notifications for high-scoring jobs
                        if enable_notifications and (job["relevance_score"] >= 15 or job.get("resume_match_score", 0) >= 20):
                            notification_result = notifications.notify_job_match(
                                job, job["relevance_score"], job.get("resume_match_score", 0)
                            )
                            job["notification_sent"] = notification_result
                    except Exception as e:
                        print(f"Notification processing failed: {e}")
                
                unique_jobs.append(job)
        
        # Sort by relevance score (highest first) and return top results
        unique_jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return unique_jobs[:limit]
        
    except Exception as e:
        print(f"Enhanced job search failed, falling back to Remotive only: {e}")
        # Fallback to Remotive-only search
        return await search_jobs_remotive_only(query, limit)


def generate_cover_letter_sync(resume_text: str, job: Dict, openai_client=None) -> str:
    """Generate a cover letter synchronously using customizable rubrics.

    Uses OpenAI ChatCompletion with rubrics-based prompts. Falls back to template if not available.
    """
    from .rubrics import rubrics
    
    # Use rubrics to generate the prompt
    prompt = rubrics.get_cover_letter_prompt(job, resume_text)
    
    job_title = job.get('title', 'Unknown Position')
    company = job.get('company', 'the Company')

    # Try OpenAI with modern client
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
            
        except ImportError:
            # Try legacy openai
            try:
                import openai
                openai.api_key = OPENAI_API_KEY
                resp = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.3,
                )
                return resp.choices[0].message.content.strip()
            except Exception:
                pass
        except Exception as e:
            print(f"OpenAI API error: {e}")

    # Enhanced template for technical roles (fallback)
    template = (
        f"Dear Hiring Manager at {company},\n\n"
        f"I am excited to apply for the {job_title} position. With extensive experience in data engineering, cloud platforms, and ML operations, "
        f"I am well-positioned to contribute to your team's technical objectives and drive scalable data solutions.\n\n"
        f"In my previous roles, I have successfully:\n"
        f"• Built and optimized data pipelines processing TB-scale datasets using Apache Spark, Kafka, and cloud-native services\n"
        f"• Implemented MLOps workflows with containerization, CI/CD, and monitoring for production ML systems\n"
        f"• Architected cloud infrastructure on AWS/Azure/GCP using Infrastructure as Code (Terraform, CloudFormation)\n\n"
        f"I would welcome the opportunity to discuss how my technical expertise aligns with {company}'s data and infrastructure needs. "
        f"Thank you for considering my application.\n\n"
        f"Best regards,\n[Your Name]\n\n"
        f"P.S. Please find my detailed technical projects and certifications in the attached resume."
    )
    return template


async def generate_cover_letter(resume_text: str, job: Dict) -> str:
    # wrapper to keep API async-friendly
    return generate_cover_letter_sync(resume_text, job)
