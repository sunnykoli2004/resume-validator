# Resume Matcher

Compares a user's PDF resume against live job listings fetched by the jobspy-test scraper, using Claude AI.

## Setup

Make sure jobspy-test API is running first:
```
cd D:\new intern\jobspy-test
uvicorn main:app --reload --port 8000
```

Then in a new terminal, activate your venv and install dependencies:
```
. "D:\new intern\venv\Scripts\Activate.ps1"
cd "D:\new intern\resume-matcher"
pip install -r requirements.txt
```

Add your Claude API key as an environment variable:
```
$env:ANTHROPIC_API_KEY = "your-api-key-here"
```

Start the resume matcher API:
```
uvicorn main:app --reload --port 8001
```

## Usage

POST to `http://127.0.0.1:8001/match` with:
- `resume` — PDF file
- `job_role` — e.g. "software engineer"
- `location` — e.g. "qatar"

## Response

Returns a list of jobs sorted by match score with:
- `match_score` — 0 to 100
- `matched_skills` — skills found in both resume and job
- `missing_skills` — skills missing from resume
- `suggestions` — improvement tips (only if score < 80%)
- `is_good_match` — true if score >= 80
