"""Agent logic: job search and cover letter generation.

Specialized for Data Engineering, MLOps, and Cloud Engineering roles.
- search_jobs(query): uses Remotive public API with priority search terms.
- generate_cover_letter(resume_text, job): uses OpenAI ChatCompletion to generate tailored cover letters.

Focuses on high-priority job types: Data Engineering, MLOps, Cloud Engineering.
"""
from typing import List, Dict, Optional
import os
import httpx

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


async def search_jobs(query: str, limit: int = 10, resume_text: str = "", enable_notifications: bool = False) -> List[Dict]:
    """Search jobs using Remotive public API, prioritizing DE/MLOps/Cloud roles.

    Returns a list of normalized job dicts, sorted by relevance to target job types.
    Optionally sends notifications for high-scoring jobs.
    """
    # If no specific query, use our priority terms
    if not query or query.strip() == "":
        query = "data engineer OR mlops OR cloud engineer OR devops"
    
    params = {"search": query}
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(REMOTIVE_SEARCH_URL, params=params)
        r.raise_for_status()
        data = r.json()

    jobs = []
    for item in data.get("jobs", [])[:limit*2]:  # Get extra jobs to filter/sort
        job = {
            "id": item.get("id"),
            "title": item.get("title"),
            "company": item.get("company_name"),
            "location": item.get("candidate_required_location"),
            "url": item.get("url"),
            "description": item.get("description"),
        }
        # Add relevance score
        job["relevance_score"] = _score_job_relevance(job.get("title", ""), job.get("description", ""))
        
        # Add resume match score and send notifications if enabled
        if resume_text:
            from .notifications import calculate_resume_match_score, notifications
            job["resume_match_score"] = calculate_resume_match_score(job, resume_text)
            
            # Send notifications for high-scoring jobs
            if enable_notifications and (job["relevance_score"] >= 15 or job["resume_match_score"] >= 20):
                notification_result = notifications.notify_job_match(
                    job, job["relevance_score"], job["resume_match_score"]
                )
                job["notification_sent"] = notification_result
        
        jobs.append(job)
    
    # Sort by relevance score (highest first) and return top results
    jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return jobs[:limit]


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
