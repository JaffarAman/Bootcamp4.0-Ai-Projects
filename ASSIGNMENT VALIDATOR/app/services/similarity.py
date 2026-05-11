from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import submitted_col

def calculate_similarity(new_text: str, student_id: str) -> float:

    prev_submissions = list(submitted_col.find({
        "student": student_id
    }))

    if not prev_submissions:
        return 0.0

    old_texts = [
        s.get("scraped_content", "") 
        for s in prev_submissions 
        if s.get("scraped_content")
    ]

    if not old_texts:
        return 0.0

    vectorizer = TfidfVectorizer().fit_transform([new_text] + old_texts)
    vectors = vectorizer.toarray()

    scores = cosine_similarity([vectors[0]], vectors[1:])
    return max(scores[0])