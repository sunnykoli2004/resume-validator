from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from datetime import date
from scraper import fetch_jobs
from save_jobs import save_jobs_to_db

SUPPORTED_SITES = [
    "indeed",
    "linkedin",
    "zip_recruiter",
    "glassdoor",
    "google",
]

app = FastAPI(title="JobSpy API", version="1.0")

@app.get("/jobs")
def get_jobs(
    job_title: str = Query(...),
    location: str = Query(...),
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

    jobs = fetch_jobs(
        job_title=job_title,
        location=location,
        companies=companies,
        sites=selected_sites,
        limit=limit,
        posted_after=posted_after,
        remote=remote,
    )

    print(f"📥 Jobs fetched: {len(jobs)}")

    saved_count = save_jobs_to_db(jobs)

    print(f"📦 Jobs saved to DB: {saved_count}")

    return {
        "sources": selected_sites,
        "count": len(jobs),
        "saved": saved_count,
        "jobs": jobs,
    }
