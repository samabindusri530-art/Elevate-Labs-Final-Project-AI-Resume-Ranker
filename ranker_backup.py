import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_similarity(resume_text, job_description):
    documents = [
        preprocess_text(job_description),
        preprocess_text(resume_text)
    ]

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    return round(float(similarity) * 100, 2)


def rank_resumes(resumes, job_description):
    results = []

    for resume in resumes:
        score = calculate_similarity(resume["text"], job_description)

        results.append({
            "filename": resume["filename"],
            "score": score
        })

    results.sort(key=lambda item: item["score"], reverse=True)

    for position, result in enumerate(results, start=1):
        result["rank"] = position

    return results
