from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_similarity(resume_text: str, jd_text: str) -> float:
    embeddings = model.encode([resume_text, jd_text])
    similarity_score = cos_sim(embeddings[0], embeddings[1]).item()
    similarity_percentage = round(similarity_score * 100, 1)
    return similarity_percentage