SKILL_SYNONYMS = {
    "python": ["python"],
    "machine learning": ["machine learning", "ml"],
    "nlp": ["nlp", "natural language processing"],
    "sql": ["sql"],
    "flask": ["flask"],
    "django": ["django"],
    "data science": ["data science"],
    "git": ["git", "github"],
    "docker": ["docker"],
    "aws": ["aws", "amazon web services"],
    "deep learning": ["deep learning", "dl"]
}

def extract_skills(text):
    text = text.lower()
    found = set()

    for skill, variants in SKILL_SYNONYMS.items():
        for v in variants:
            if v in text:
                found.add(skill)

    return list(found)
