import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MATCH_THRESHOLD = 80

# Common tech skills and keywords to track
SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust",
    "react", "angular", "vue", "node", "django", "fastapi", "flask", "spring",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "linux",
    "machine learning", "deep learning", "nlp", "data science", "pandas", "numpy",
    "git", "ci/cd", "agile", "scrum", "rest", "graphql", "microservices",
    "communication", "leadership", "teamwork", "problem solving",
    "html", "css", "figma", "excel", "tableau", "power bi",
]


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            found.append(skill)
    return found


def get_match_score(resume_text: str, job_text: str) -> int:
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf = vectorizer.fit_transform([
            clean_text(resume_text),
            clean_text(job_text)
        ])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(score * 100)
    except Exception:
        return 0


def generate_suggestions(missing_skills: list, match_score: int) -> list:
    suggestions = []

    if missing_skills:
        suggestions.append(
            f"Add these missing skills to your resume: {', '.join(missing_skills[:5])}"
        )

    if match_score < 50:
        suggestions.append(
            "Your resume needs significant updates for this role. Consider tailoring it specifically for this job."
        )
    elif match_score < 80:
        suggestions.append(
            "Add more relevant keywords from the job description to your resume."
        )

    suggestions.append(
        "Use the job description's exact wording where applicable — many companies use ATS keyword scanning."
    )
    suggestions.append(
        "Add measurable achievements (e.g. 'Reduced load time by 40%') to strengthen your resume."
    )
    suggestions.append(
        "Make sure your resume has a clear summary section matching the job requirements."
    )

    return suggestions[:5]


async def compare_resume_to_jobs(resume_text: str, jobs: list) -> list:
    results = []

    resume_skills = extract_skills(resume_text)

    for job in jobs:
        job_title = job.get("title", "Unknown Role")
        company = job.get("company", "Unknown Company")
        description = job.get("description", "")

        if not description:
            continue

        # Calculate match score
        match_score = get_match_score(resume_text, description)

        # Find matched and missing skills
        job_skills = extract_skills(description)
        matched_skills = [s for s in resume_skills if s in job_skills]
        missing_skills = [s for s in job_skills if s not in resume_skills]

        # Generate summary
        if match_score >= 80:
            summary = f"Strong match! Your resume aligns well with this {job_title} role."
        elif match_score >= 50:
            summary = f"Moderate match. Some gaps exist between your resume and this {job_title} role."
        else:
            summary = f"Low match. Your resume needs significant tailoring for this {job_title} role."

        result = {
            "job_title": job_title,
            "company": company,
            "job_url": job.get("job_url", ""),
            "location": job.get("location", ""),
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills[:10],
            "summary": summary,
            "is_good_match": match_score >= MATCH_THRESHOLD,
        }

        if match_score < MATCH_THRESHOLD:
            result["suggestions"] = generate_suggestions(missing_skills, match_score)

        results.append(result)

    # Sort by match score
    results.sort(key=lambda x: x.get("match_score", 0), reverse=True)

    return results
