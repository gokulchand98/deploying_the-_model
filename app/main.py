"""FastAPI backend exposing endpoints for the job-search agent."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from . import agent, db

app = FastAPI(title="Job Search Agent API")


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10


class CoverLetterRequest(BaseModel):
    job: dict
    resume_text: str


class ApplyRequest(BaseModel):
    job: dict
    notes: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    db.init_db()


@app.post("/api/search")
async def api_search(req: SearchRequest):
    try:
        jobs = await agent.search_jobs(req.query, limit=req.limit)
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


# Simple health
@app.get("/api/health")
async def health():
    return {"status": "ok"}
