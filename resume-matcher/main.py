import os
import sys

from fastapi import FastAPI, Query, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import date
import pdfplumber

# 1. ADD THE PATH FIX HERE (At the top of the file)
scraper_path = r"D:\new intern\jobspy-test"
if scraper_path not in sys.path:
    sys.path.append(scraper_path)

# 2. NOW the imports will work without the ModuleNotFoundError
from scraper import fetch_jobs
from save_jobs import save_jobs_to_db
from matcher import compare_resume_to_jobs

SUPPORTED_SITES = [
    "indeed",
    "linkedin",
    "zip_recruiter",
    "glassdoor",
    "google",
]

app = FastAPI(title="JobSpy API", version="1.0")
app = FastAPI()

# ADD THIS BLOCK HERE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CORS SETUP (Crucial for frontend connection) ---
# This allows your frontend (running on a different port or file) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# PHASE 1: SEARCH AND SCRAPE JOBS
# ==========================================
@app.get("/jobs")
def get_jobs(
    job_title: str = Query(...),
    location: str = Query(...),
    country: Optional[str] = Query(None),
    companies: Optional[List[str]] = Query(None),
    sites: Optional[List[str]] = Query(None),
    limit: int = Query(20, le=100),
    posted_after: Optional[date] = Query(None),
    remote: Optional[bool] = Query(None),
):
    selected_sites = sites or SUPPORTED_SITES

    invalid = set(selected_sites) - set(SUPPORTED_SITES)
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sites: {', '.join(invalid)}"
        )

    # 1. Scrape the jobs
    jobs = fetch_jobs(
        job_title=job_title,
        location=location,
        country=country,
        companies=companies,
        sites=selected_sites,
        limit=limit,
        posted_after=posted_after,
        remote=remote,
    )

    print(f"📥 Jobs fetched: {len(jobs)}")

    # 2. Save to database
    saved_count = save_jobs_to_db(jobs)

    print(f"📦 Jobs saved to DB: {saved_count}")

    # 3. Return to frontend
    return {
        "sources": selected_sites,
        "count": len(jobs),
        "saved": saved_count,
        "jobs": jobs,
    }


# ==========================================
# PHASE 2: MATCH RESUME TO A SINGLE JOB
# ==========================================
@app.post("/match_single_job")
async def match_single_job(
    resume: UploadFile = File(...),
    job_title: str = Form(...),
    company: str = Form(...),
    description: str = Form(...)
):
    # 1. Extract text from the uploaded PDF
    resume_text = ""
    try:
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    resume_text += extracted + "\n"
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not read PDF file.")

    # 2. Format the single job into the list structure your matcher expects
    single_job_list = [{
        "title": job_title,
        "company": company,
        "description": description
    }]

    # 3. Run your existing matcher function
    match_results = await compare_resume_to_jobs(resume_text, single_job_list)

    # 4. Return the result back to the frontend
    if match_results:
        return match_results[0]
    
    return {"error": "Could not generate match."}