from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def cosine_similarity(a: np.ndarray, b: np.ndarray):
    return np.dot(a, b)

def get_embeddings(texts: list[str]):
    if not isinstance(texts, list) or not all(isinstance(x, str) for x in texts):
        raise TypeError("texts must be list[str]")
    
    vectors = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return vectors