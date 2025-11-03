"""
Notification system for job alerts via SMS and phone calls.

Integrates with Twilio to send:
- SMS alerts for job matches above threshold
- Phone calls for jobs that highly match your resume
"""
import os
from typing import Dict, Optional
import logging
from datetime import datetime

# Twilio configuration from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN") 
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Your Twilio number
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER")      # Your personal number

# Notification thresholds
SMS_THRESHOLD = int(os.getenv("SMS_THRESHOLD", "15"))     # Send SMS for jobs scoring 15+
CALL_THRESHOLD = int(os.getenv("CALL_THRESHOLD", "30"))   # Call for jobs scoring 30+

logger = logging.getLogger(__name__)

class NotificationManager:
    """Handles SMS and phone call notifications for job matches"""
    
    def __init__(self):
        self.twilio_client = None
        self.setup_twilio()
    
    def setup_twilio(self):
        """Initialize Twilio client if credentials are available"""
        try:
            if all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, YOUR_PHONE_NUMBER]):
                from twilio.rest import Client
                self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                logger.info("✅ Twilio notifications enabled")
            else:
                logger.warning("⚠️ Twilio credentials not configured - notifications disabled")
        except ImportError:
            logger.error("❌ Twilio library not installed")
        except Exception as e:
            logger.error(f"❌ Twilio setup failed: {e}")
    
    def send_sms(self, message: str) -> bool:
        """Send SMS notification"""
        if not self.twilio_client:
            logger.warning("SMS not sent - Twilio not configured")
            return False
        
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=YOUR_PHONE_NUMBER
            )
            logger.info(f"📱 SMS sent: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"❌ SMS failed: {e}")
            return False
    
    def make_call(self, message: str) -> bool:
        """Make phone call with TTS message"""
        if not self.twilio_client:
            logger.warning("Call not made - Twilio not configured")
            return False
        
        try:
            # Create TwiML for the call
            twiml_message = f"<Response><Say voice='alice'>{message}</Say></Response>"
            
            call = self.twilio_client.calls.create(
                twiml=twiml_message,
                to=YOUR_PHONE_NUMBER,
                from_=TWILIO_PHONE_NUMBER
            )
            logger.info(f"📞 Call initiated: {call.sid}")
            return True
        except Exception as e:
            logger.error(f"❌ Call failed: {e}")
            return False
    
    def notify_job_match(self, job: Dict, score: int, resume_match_score: Optional[int] = None) -> Dict:
        """Send appropriate notification based on job score and resume match"""
        notifications_sent = {
            "sms_sent": False,
            "call_made": False,
            "reason": "No notification threshold met"
        }
        
        job_title = job.get('title', 'Unknown Position')
        company = job.get('company', 'Unknown Company')
        location = job.get('location', 'Unknown Location')
        job_url = job.get('url', '')
        
        # Determine if we should call (high resume match)
        should_call = False
        if resume_match_score and resume_match_score >= CALL_THRESHOLD:
            should_call = True
            notifications_sent["reason"] = f"High resume match (score: {resume_match_score})"
        elif score >= CALL_THRESHOLD:
            should_call = True
            notifications_sent["reason"] = f"High job score (score: {score})"
        
        # Make phone call for high-priority matches
        if should_call:
            call_message = (
                f"High priority job match found! "
                f"{job_title} at {company}. "
                f"Job score: {score}. "
                f"Resume match: {resume_match_score or 'Not calculated'}. "
                f"Check your job agent dashboard for details."
            )
            notifications_sent["call_made"] = self.make_call(call_message)
        
        # Send SMS for good matches (if we haven't called)
        elif score >= SMS_THRESHOLD:
            sms_message = (
                f"🎯 Job Match Alert!\n\n"
                f"📋 {job_title}\n"
                f"🏢 {company}\n"  
                f"📍 {location}\n"
                f"⭐ Score: {score}/100\n"
                f"🔗 {job_url[:50]}{'...' if len(job_url) > 50 else ''}\n\n"
                f"Check your agent dashboard!"
            )
            notifications_sent["sms_sent"] = self.send_sms(sms_message)
            notifications_sent["reason"] = f"Job score above SMS threshold ({score})"
        
        return notifications_sent
    
    def send_daily_summary(self, jobs_found: int, applications_made: int) -> bool:
        """Send daily summary SMS"""
        message = (
            f"📊 Daily Job Agent Summary\n"
            f"🔍 Jobs Found: {jobs_found}\n"
            f"📝 Applications: {applications_made}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        return self.send_sms(message)
    
    def test_notifications(self) -> Dict:
        """Test both SMS and call functionality"""
        results = {
            "sms_test": False,
            "call_test": False,
            "configured": self.twilio_client is not None
        }
        
        if self.twilio_client:
            # Test SMS
            test_sms = "🧪 Test SMS from your Job Search Agent! Notifications are working."
            results["sms_test"] = self.send_sms(test_sms)
            
            # Test Call
            test_call_message = "This is a test call from your Job Search Agent. Notifications are configured correctly."
            results["call_test"] = self.make_call(test_call_message)
        
        return results

# Global notification manager instance
notifications = NotificationManager()


def calculate_resume_match_score(job: Dict, resume_text: str) -> int:
    """Calculate how well a job matches the resume content"""
    if not resume_text:
        return 0
    
    score = 0
    job_desc = job.get('description', '').lower()
    resume_lower = resume_text.lower()
    
    # Extract key technologies/skills from resume
    resume_skills = []
    skill_keywords = [
        'python', 'java', 'scala', 'sql', 'spark', 'kafka', 'airflow', 
        'kubernetes', 'docker', 'aws', 'azure', 'gcp', 'terraform',
        'databricks', 'snowflake', 'redshift', 'bigquery', 'dbt',
        'mlops', 'machine learning', 'data engineering', 'devops'
    ]
    
    for skill in skill_keywords:
        if skill in resume_lower:
            resume_skills.append(skill)
    
    # Score based on matching skills mentioned in job
    for skill in resume_skills:
        if skill in job_desc:
            score += 5
    
    # Bonus for experience level matching
    if 'senior' in resume_lower and 'senior' in job_desc:
        score += 10
    if 'lead' in resume_lower and 'lead' in job_desc:
        score += 8
    if 'staff' in resume_lower and 'staff' in job_desc:
        score += 12
    
    return min(score, 100)  # Cap at 100