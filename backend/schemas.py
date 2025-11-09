from pydantic import BaseModel
from typing import Optional, List

# Users
class UserIn(BaseModel):
    name: str
    role: str
    email: str
    summary: Optional[str] = ""
    skills: Optional[str] = ""
    interests: Optional[str] = ""
    links: Optional[str] = ""

class UserOut(UserIn):
    id: int
    class Config: from_attributes = True

# Projects
class ProjectIn(BaseModel):
    owner_id: int
    title: str
    description: str
    tags: Optional[str] = ""

class ProjectOut(ProjectIn):
    id: int
    stack: str = ""
    class Config: from_attributes = True

class ProjectApproveIn(BaseModel):
    project_id: int
    stack: List[str]

# Matching / Peers (for completeness)
class StudentQuery(BaseModel):
    user_id: int
    interests: Optional[str] = ""
    skills: Optional[str] = ""

# LLM
class StackDraft(BaseModel):
    stack: List[str]
    skills: List[str]
    evaluation: List[str]
