from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.skills import extract_skills

def calculate_similarity(job_desc, resume_text):
    job_desc = job_desc or ""
    resume_text = resume_text or ""

    job_skills = set(extract_skills(job_desc))
    resume_skills = set(extract_skills(resume_text))

    skill_score = 0
    if job_skills:
        skill_score = len(job_skills & resume_skills) / len(job_skills)

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=300
    )

    vectors = vectorizer.fit_transform([job_desc, resume_text])
    text_score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    final_score = (0.8 * skill_score) + (0.2 * text_score)


    # ALWAYS returns a tuple
    return float(final_score), list(resume_skills)
