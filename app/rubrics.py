"""
Rubrics system for customizable agent behavior.

This module allows you to define custom rules and criteria for:
- Job evaluation and scoring
- Cover letter generation prompts
- Application decision making
- Search prioritization

You can easily update these rubrics to change how your agent operates.
"""
import json
from typing import Dict, List, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import os

@dataclass
class JobScoringRubric:
    """Defines how jobs are scored and prioritized"""
    title_keywords: Dict[str, int]  # keyword -> score weight
    description_keywords: Dict[str, int]
    company_preferences: Dict[str, int]  # company -> bonus points
    location_preferences: Dict[str, int]  # location type -> bonus points
    min_score_threshold: int = 5
    
@dataclass
class CoverLetterRubric:
    """Defines how cover letters are generated"""
    tone: str = "professional"  # professional, casual, enthusiastic
    length: str = "medium"  # short, medium, long
    focus_areas: List[str] = None  # technical_skills, achievements, culture_fit
    custom_instructions: str = ""
    signature_style: str = "formal"
    
@dataclass  
class ApplicationRubric:
    """Defines application decision criteria"""
    auto_apply_score_threshold: int = 20
    skip_companies: List[str] = None
    required_keywords: List[str] = None
    blacklist_keywords: List[str] = None
    
class RubricsManager:
    """Manages all agent behavior rubrics"""
    
    def __init__(self, config_path: str = "config/rubrics.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(exist_ok=True)
        self.load_rubrics()
    
    def load_rubrics(self):
        """Load rubrics from config file or create defaults"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            self.job_scoring = JobScoringRubric(**data.get('job_scoring', {}))
            self.cover_letter = CoverLetterRubric(**data.get('cover_letter', {}))
            self.application = ApplicationRubric(**data.get('application', {}))
        else:
            # Create default rubrics
            self.create_default_rubrics()
            self.save_rubrics()
    
    def create_default_rubrics(self):
        """Create default DE/MLOps/Cloud focused rubrics"""
        self.job_scoring = JobScoringRubric(
            title_keywords={
                # Data Engineering
                "data engineer": 15,
                "data engineering": 15,
                "senior data engineer": 20,
                "lead data engineer": 18,
                "staff data engineer": 22,
                "principal data engineer": 25,
                
                # MLOps
                "mlops": 18,
                "ml engineer": 16,
                "machine learning engineer": 16,
                "ml platform": 14,
                "ai engineer": 14,
                
                # Cloud Engineering  
                "cloud engineer": 16,
                "devops engineer": 14,
                "platform engineer": 15,
                "infrastructure engineer": 13,
                "site reliability engineer": 14,
                "sre": 14,
            },
            description_keywords={
                # Technical Skills - High Value
                "apache spark": 8,
                "kafka": 7,
                "airflow": 7,
                "kubernetes": 8,
                "docker": 6,
                "terraform": 7,
                "aws": 6,
                "azure": 6,
                "gcp": 6,
                "databricks": 8,
                "snowflake": 7,
                "dbt": 6,
                
                # ML/AI Skills
                "mlflow": 7,
                "kubeflow": 8,
                "sagemaker": 6,
                "pytorch": 5,
                "tensorflow": 5,
                
                # Programming Languages
                "python": 4,
                "scala": 5,
                "java": 4,
                "sql": 3,
                
                # Methodologies
                "ci/cd": 5,
                "iac": 6,
                "infrastructure as code": 6,
                "data pipeline": 6,
                "etl": 5,
                "streaming": 6,
            },
            company_preferences={
                # Add your preferred companies here
                "netflix": 5,
                "spotify": 5,
                "uber": 4,
                "meta": 4,
                "google": 5,
                "microsoft": 4,
                "amazon": 3,
            },
            location_preferences={
                "remote": 8,
                "hybrid": 5,
                "san francisco": 3,
                "new york": 3,
                "seattle": 3,
                "austin": 4,
            },
            min_score_threshold=8
        )
        
        self.cover_letter = CoverLetterRubric(
            tone="professional",
            length="medium",
            focus_areas=["technical_skills", "achievements", "specific_experience"],
            custom_instructions="Emphasize hands-on experience with data pipelines, cloud platforms, and ML systems. Mention specific technologies from the job description. Show quantifiable impact where possible.",
            signature_style="professional"
        )
        
        self.application = ApplicationRubric(
            auto_apply_score_threshold=25,  # Very high threshold for auto-apply
            skip_companies=["companies_with_bad_culture"],  # Add companies to skip
            required_keywords=["data", "engineering", "cloud", "ml"],  # Must have at least one
            blacklist_keywords=["unpaid", "internship", "entry level"]  # Avoid these
        )
    
    def save_rubrics(self):
        """Save current rubrics to config file"""
        data = {
            'job_scoring': asdict(self.job_scoring),
            'cover_letter': asdict(self.cover_letter), 
            'application': asdict(self.application)
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_rubrics_from_instructions(self, instructions: str):
        """Update rubrics based on natural language instructions"""
        # This is where you can add your custom rubrics logic
        # For now, it saves the instructions for manual processing
        
        instructions_file = self.config_path.parent / "custom_instructions.txt"
        with open(instructions_file, 'w') as f:
            f.write(f"Instructions received at {os.popen('date').read().strip()}:\n\n")
            f.write(instructions)
            f.write("\n\n--- Previous Instructions ---\n")
            if instructions_file.exists():
                f.write(open(instructions_file).read())
        
        return f"Instructions saved to {instructions_file}. Update the rubrics manually or implement NLP parsing."
    
    def get_job_score(self, job: Dict) -> int:
        """Calculate job score based on current rubrics"""
        score = 0
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        company = job.get('company', '').lower()
        location = job.get('location', '').lower()
        
        # Score based on title keywords
        for keyword, weight in self.job_scoring.title_keywords.items():
            if keyword.lower() in title:
                score += weight
        
        # Score based on description keywords  
        for keyword, weight in self.job_scoring.description_keywords.items():
            if keyword.lower() in description:
                score += weight
        
        # Company preferences
        for pref_company, bonus in self.job_scoring.company_preferences.items():
            if pref_company.lower() in company:
                score += bonus
                
        # Location preferences
        for pref_location, bonus in self.job_scoring.location_preferences.items():
            if pref_location.lower() in location:
                score += bonus
        
        return score
    
    def should_auto_apply(self, job: Dict, score: int) -> bool:
        """Determine if job meets auto-apply criteria"""
        if score < self.application.auto_apply_score_threshold:
            return False
            
        # Check blacklist
        description = job.get('description', '').lower()
        title = job.get('title', '').lower()
        
        if self.application.blacklist_keywords:
            for blacklist_word in self.application.blacklist_keywords:
                if blacklist_word.lower() in description or blacklist_word.lower() in title:
                    return False
        
        # Check required keywords
        if self.application.required_keywords:
            has_required = any(
                req_keyword.lower() in description or req_keyword.lower() in title
                for req_keyword in self.application.required_keywords
            )
            if not has_required:
                return False
        
        return True
    
    def get_cover_letter_prompt(self, job: Dict, resume: str) -> str:
        """Generate customized cover letter prompt based on rubrics"""
        base_prompt = f"""
Write a {self.cover_letter.length} cover letter in a {self.cover_letter.tone} tone for this job:

Job Title: {job.get('title')}
Company: {job.get('company')}
Location: {job.get('location')}

Job Description:
{job.get('description', '')[:1500]}

Candidate Background:
{resume[:2000]}

Focus Areas: {', '.join(self.cover_letter.focus_areas or [])}

Custom Instructions: {self.cover_letter.custom_instructions}

Requirements:
- Use {self.cover_letter.signature_style} signature style
- Highlight relevant technical skills mentioned in the job description
- Show specific achievements and quantifiable impact
- End with professional closing and call to action
"""
        return base_prompt.strip()

# Global rubrics manager instance
rubrics = RubricsManager()