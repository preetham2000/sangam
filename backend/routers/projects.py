from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Project
from ..schemas import ProjectIn, ProjectOut, ProjectApproveIn
from ..services.llm import draft_stack_for_project

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectOut)
def create_project(body: ProjectIn, db: Session = Depends(get_db)):
    p = Project(**body.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.post("/{pid}/draft_stack")
def draft_stack(pid: int, db: Session = Depends(get_db)):
    p = db.get(Project, pid)
    if not p:
        raise HTTPException(404, "Project not found")
    out = draft_stack_for_project(p.description)
    return out

@router.post("/approve_stack", response_model=ProjectOut)
def approve_stack(body: ProjectApproveIn, db: Session = Depends(get_db)):
    p = db.get(Project, body.project_id)
    if not p:
        raise HTTPException(404, "Project not found")
    p.stack = ",".join(body.stack)
    db.add(p); db.commit(); db.refresh(p)
    return p
