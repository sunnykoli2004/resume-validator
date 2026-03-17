import json
import pandas as pd
from jobspy import scrape_jobs

jobs_df = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter"],
    search_term="software engineer",
    location="San Francisco, CA",
    results_wanted=50
)

print("Rows:", len(jobs_df))

# 🔥 Convert date/datetime columns to string
for col in jobs_df.columns:
    if pd.api.types.is_datetime64_any_dtype(jobs_df[col]):
        jobs_df[col] = jobs_df[col].astype(str)

# 🔥 Also handle Python date objects
jobs_df = jobs_df.map(
    lambda x: x.isoformat() if hasattr(x, "isoformat") else x
)

# Replace NaN with empty string
jobs_json = jobs_df.fillna("").to_dict(orient="records")

with open("jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs_json, f, indent=2, ensure_ascii=False)

print("✅ jobs.json created successfully")
