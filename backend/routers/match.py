from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Project, User
from ..services.embeddings import embed_texts, cosine_rank

router = APIRouter(prefix="/match", tags=["match"])

def pack_profile(s: User) -> str:
    return f"Name: {s.name}\nSummary: {s.summary}\nSkills: {s.skills}\nInterests: {s.interests}"

@router.get("/project/{pid}")
def match_students_for_project(pid: int, topk: int = 5, db: Session = Depends(get_db)):
    proj = db.get(Project, pid)
    if not proj:
        raise HTTPException(404, "Project not found")

    students = db.scalars(select(User).where(User.role == "student")).all()
    if not students:
        return []

    query_text = f"{proj.title}\n{proj.description}\nStack: {proj.stack}\nTags: {proj.tags}"
    qv = embed_texts([query_text])[0]

    corpus = [pack_profile(s) for s in students]
    M = embed_texts(corpus)

    order = cosine_rank(qv, M)[:topk]
    ranked = [students[i] for i in order]
    # Return plain dicts to match your Streamlit consumption
    return [
        {
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "summary": s.summary,
            "skills": s.skills,
            "interests": s.interests,
        }
        for s in ranked
    ]
