from typing import List
import numpy as np

# existing: embed(), cosine_rank(), pack_profile()

def pack_project(title: str, description: str, tags: str | None, stack: str | None) -> str:
    t = [
        f"Title: {title or ''}".strip(),
        f"Description: {description or ''}".strip(),
        f"Tags: {tags or ''}".strip(),
        f"Stack: {stack or ''}".strip(),
    ]
    return "\n".join(t)

def topk_by_cosine(query_text: str, corpus_texts: List[str], k: int = 5):
    qv = embed([query_text])[0]
    M = embed(corpus_texts)
    order = cosine_rank(qv, M)[:k]
    return order
