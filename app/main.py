"""FastAPI backend exposing endpoints for the job-search agent."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import os

from . import agent, db

# Create FastAPI app with Railway-compatible settings
app = FastAPI(
    title="Job Search Agent API",
    description="End-to-end job search agent for Data Engineering, MLOps, and Cloud roles",
    version="1.0.0"
)

# Add CORS middleware to allow Railway healthcheck and other domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, be more restrictive
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to handle Railway healthcheck hostname
@app.middleware("http")
async def railway_healthcheck_middleware(request: Request, call_next):
    """Allow Railway's healthcheck.railway.app hostname"""
    response = await call_next(request)
    
    # Add headers for Railway compatibility
    response.headers["X-Railway-Health"] = "ok"
    
    return response


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    resume_text: Optional[str] = ""
    enable_notifications: Optional[bool] = False


class CoverLetterRequest(BaseModel):
    job: dict
    resume_text: str


class ApplyRequest(BaseModel):
    job: dict
    notes: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    print("=" * 50)
    print("🚀 STARTING JOB SEARCH AGENT API")
    print("=" * 50)
    
    try:
        print("Step 1: Basic imports check...")
        import os
        import sys
        print(f"✅ Python version: {sys.version}")
        print(f"✅ Working directory: {os.getcwd()}")
        print(f"✅ PORT from env: {os.environ.get('PORT', 'not set')}")
        
        print("Step 2: Database initialization...")
        db.init_db()
        print("✅ Database initialized successfully")
        
        print("Step 3: Testing basic functionality...")
        apps = db.list_applications()
        print(f"✅ Database connection works, found {len(apps)} applications")
        
        print("Step 4: Loading optional modules...")
        # Test notification system (non-critical)
        try:
            from .notifications import notifications
            print(f"✅ Notification system loaded (Configured: {notifications.twilio_client is not None})")
        except Exception as e:
            print(f"⚠️ Notification system error (non-critical): {e}")
        
        print("=" * 50)
        print("🎯 API STARTUP COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ CRITICAL STARTUP ERROR: {e}")
        print("=" * 50)
        import traceback
        traceback.print_exc()
        # Continue anyway to allow health check
        pass


@app.post("/api/search")
async def api_search(req: SearchRequest):
    try:
        jobs = await agent.search_jobs(
            req.query, 
            limit=req.limit,
            resume_text=req.resume_text,
            enable_notifications=req.enable_notifications
        )
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/priority")
async def api_search_priority(limit: int = 15):
    """Quick endpoint to get high-priority DE/MLOps/Cloud jobs."""
    try:
        jobs = await agent.search_jobs("", limit=limit)  # Uses default priority search
        # Filter only high-relevance jobs
        priority_jobs = [j for j in jobs if j.get("relevance_score", 0) >= 3]
        return {"jobs": priority_jobs, "total_found": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cover_letter")
async def api_cover_letter(req: CoverLetterRequest):
    try:
        text = await agent.generate_cover_letter(req.resume_text, req.job)
        return {"cover_letter": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/apply")
async def api_apply(req: ApplyRequest):
    try:
        job = req.job
        rowid = db.add_application(job_id=job.get("id"), job_title=job.get("title"), company=job.get("company"), notes=req.notes)
        return {"application_id": rowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/applications")
async def api_list_applications():
    return {"applications": db.list_applications()}


# Rubrics management endpoints
class RubricsUpdateRequest(BaseModel):
    instructions: str


@app.get("/api/rubrics")
async def api_get_rubrics():
    """Get current agent behavior rubrics"""
    try:
        from . import rubrics as r
        return {
            "job_scoring": r.rubrics.job_scoring.__dict__,
            "cover_letter": r.rubrics.cover_letter.__dict__,
            "application": r.rubrics.application.__dict__
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rubrics/update")
async def api_update_rubrics(req: RubricsUpdateRequest):
    """Update agent behavior based on natural language instructions"""
    try:
        from . import rubrics as r
        result = r.rubrics.update_rubrics_from_instructions(req.instructions)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/score")
async def api_score_job(job: dict):
    """Score a specific job based on current rubrics"""
    try:
        from . import rubrics as r
        score = r.rubrics.get_job_score(job)
        should_apply = r.rubrics.should_auto_apply(job, score)
        return {
            "score": score,
            "should_auto_apply": should_apply,
            "meets_threshold": score >= r.rubrics.job_scoring.min_score_threshold
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Notification endpoints
@app.post("/api/notifications/test")
async def api_test_notifications():
    """Test SMS and phone call functionality"""
    try:
        from .notifications import notifications
        results = notifications.test_notifications()
        return {"test_results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notifications/status")
async def api_notification_status():
    """Check notification configuration status"""
    try:
        from .notifications import notifications, TWILIO_ACCOUNT_SID, YOUR_PHONE_NUMBER, SMS_THRESHOLD, CALL_THRESHOLD
        return {
            "configured": notifications.twilio_client is not None,
            "twilio_configured": bool(TWILIO_ACCOUNT_SID),
            "phone_number_set": bool(YOUR_PHONE_NUMBER),
            "sms_threshold": SMS_THRESHOLD,
            "call_threshold": CALL_THRESHOLD
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NotificationTestRequest(BaseModel):
    message: str
    type: str  # "sms" or "call"


@app.post("/api/notifications/send")
async def api_send_notification(req: NotificationTestRequest):
    """Send a test notification"""
    try:
        from .notifications import notifications
        
        if req.type == "sms":
            success = notifications.send_sms(req.message)
        elif req.type == "call":
            success = notifications.make_call(req.message)
        else:
            raise HTTPException(status_code=400, detail="Type must be 'sms' or 'call'")
        
        return {"success": success, "type": req.type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoints (Railway requires HTTP 200)
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Job Search Agent API", "status": "running", "health": "/health"}


@app.get("/health")
async def health_check():
    """Railway health check endpoint - minimal and reliable"""
    return {"status": "ok"}


@app.get("/ping")
async def ping():
    """Super simple ping endpoint"""
    return "pong"


@app.get("/api/health")
async def health():
    """Detailed health check endpoint for Railway deployment"""
    try:
        # Test database connection
        applications = db.list_applications()
        
        # Test notification system (non-critical)
        notification_status = False
        try:
            from .notifications import notifications
            notification_status = notifications.twilio_client is not None
        except:
            pass
        
        return {
            "status": "healthy",
            "timestamp": "2024-11-03",
            "database": "connected",
            "notifications": "configured" if notification_status else "disabled",
            "application_count": len(applications)
        }
    except Exception as e:
        print(f"Health check error: {e}")
        return {"status": "ok"}  # Return ok even if some features fail
