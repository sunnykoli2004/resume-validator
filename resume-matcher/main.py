from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io
import pandas as pd
from jobspy import scrape_jobs
from matcher import compare_resume_to_jobs

app = FastAPI(title="Resume Matcher API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

@app.post("/match")
async def match_resume(
    resume: UploadFile = File(...),
    job_role: str = Form(...),
    location: str = Form(...),
):
    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)
    print(f"📄 Resume text length: {len(resume_text)}")

    if not resume_text:
        return {"error": "Could not extract text from the PDF."}

    df = scrape_jobs(
        site_name=["indeed", "linkedin"],
        search_term=job_role,
        location=location,
        results_wanted=20,
        country_indeed=location.strip().title(),
    )

    print(f"📦 Jobs fetched: {len(df)}")

    if df.empty:
        df = scrape_jobs(
            site_name=["linkedin"],
            search_term=job_role,
            location=location,
            results_wanted=20,
        )
        print(f"📦 Fallback LinkedIn jobs: {len(df)}")

    if df.empty:
        return {"error": "No jobs found for the given role and location."}

    df = df.map(lambda x: x.isoformat() if hasattr(x, "isoformat") else x)
    jobs = df.fillna("").to_dict(orient="records")

    for j in jobs[:3]:
        print(f"  - {j.get('title')} | desc length: {len(j.get('description', ''))}")

    results = await compare_resume_to_jobs(resume_text, jobs)
    print(f"✅ Results count: {len(results)}")

    # Generate overall summary
    good_matches = [r for r in results if r.get("is_good_match")]
    avg_score = round(sum(r["match_score"] for r in results) / len(results)) if results else 0
    all_missing = []
    for r in results:
        all_missing.extend(r.get("missing_skills", []))
    top_missing = sorted(set(all_missing), key=lambda x: all_missing.count(x), reverse=True)[:5]

    overall_summary = {
        "average_match_score": avg_score,
        "good_matches_count": len(good_matches),
        "top_missing_skills": top_missing,
        "overall_advice": f"Your resume scored an average of {avg_score}% across {len(results)} jobs. "
                          f"The most commonly missing skills are: {', '.join(top_missing)}. "
                          f"Adding these to your resume will significantly improve your match rate."
    }

    return {
        "job_role": job_role,
        "location": location,
        "total_jobs_checked": len(jobs),
        "overall_summary": overall_summary,
        "results": results,
    }

@app.get("/")
def root():
    return {"message": "Resume Matcher API is running. POST to /match"}