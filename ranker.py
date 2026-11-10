import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILLS_LIST = [
    "python", "java", "c++", "c#", "javascript", "typescript",
    "sql", "mysql", "postgresql", "mongodb",
    "flask", "django", "fastapi", "html", "css", "react",
    "node.js", "machine learning", "deep learning",
    "artificial intelligence", "data analysis",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "excel", "power bi", "tableau", "git", "github",
    "docker", "aws", "azure", "linux",
    "data structures", "algorithms",
    "object-oriented programming"
]


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS_LIST:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


def calculate_similarity(resume_text, job_description):

    documents = [
        preprocess_text(job_description),
        preprocess_text(resume_text)
    ]

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )[0][0]

    return round(float(similarity) * 100, 2)


def rank_resumes(resumes, job_description):

    results = []

    required_skills = extract_skills(job_description)

    for resume in resumes:

        resume_text = resume["text"]

        similarity_score = calculate_similarity(
            resume_text,
            job_description
        )

        candidate_skills = extract_skills(resume_text)

        matched_skills = [
            skill for skill in required_skills
            if skill in candidate_skills
        ]

        missing_skills = [
            skill for skill in required_skills
            if skill not in candidate_skills
        ]

        if required_skills:

            skill_score = round(
                len(matched_skills) / len(required_skills) * 100,
                2
            )

            final_score = round(
                similarity_score * 0.70 +
                skill_score * 0.30,
                2
            )

        else:
            skill_score = 0
            final_score = similarity_score

        results.append({
            "filename": resume["filename"],
            "similarity_score": similarity_score,
            "skill_score": skill_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "score": final_score
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    for position, result in enumerate(results, start=1):
        result["rank"] = position

    return results