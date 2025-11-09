from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import get_db
from ..models import User
from ..schemas import UserIn, UserOut

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("", response_model=UserOut)
def create_profile(body: UserIn, db: Session = Depends(get_db)):
    u = User(**body.model_dump())
    db.add(u); db.commit(); db.refresh(u)
    return u

@router.get("", response_model=list[UserOut])
def list_profiles(role: str | None = None, db: Session = Depends(get_db)):
    q = select(User)
    if role:
        q = q.where(User.role == role)
    return db.scalars(q).all()
