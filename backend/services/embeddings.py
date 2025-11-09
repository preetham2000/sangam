import os
import numpy as np
from typing import List
from openai import OpenAI

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-large")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_texts(texts: List[str]) -> np.ndarray:
    if len(texts) == 0:
        return np.zeros((0, 1), dtype="float32")
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vecs = [d.embedding for d in resp.data]
    X = np.array(vecs, dtype="float32")
    # L2 normalize
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    return X / norms

def cosine_rank(query_vec: np.ndarray, matrix: np.ndarray) -> List[int]:
    sims = (matrix @ query_vec.reshape(-1, 1)).ravel()
    return list(np.argsort(-sims))
