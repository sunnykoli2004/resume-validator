import pandas as pd
from jobspy import scrape_jobs
from datetime import date

def fetch_jobs(
    job_title: str,
    location: str,
    country: str | None,
    companies: list[str] | None,
    sites: list[str],
    limit: int,
    posted_after: date | None,
    remote: bool | None,
):
    all_jobs = []

    search_targets = companies if companies else [""]

    for company in search_targets:
        search_term = f"{job_title} {company}".strip()

        df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location,
            results_wanted=limit,
            country_indeed=country.strip().title() if country else location.strip().title(),
        )

        if len(df) == 0:
            continue

        # Add searched company info
        df["searched_company"] = company

        # Filter remote
        if remote is not None:
            df = df[df["is_remote"] == remote]

        # Filter by posted date
        if posted_after and "date_posted" in df.columns:
            df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
            df = df[df["date_posted"] >= pd.Timestamp(posted_after)]

        all_jobs.append(df)

    if not all_jobs:
        return []

    final_df = pd.concat(all_jobs, ignore_index=True)

    # Convert date/datetime to string
    final_df = final_df.map(
    lambda x: x.isoformat() if hasattr(x, "isoformat") else x
)

    return final_df.fillna("").to_dict(orient="records")
