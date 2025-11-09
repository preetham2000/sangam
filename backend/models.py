# backend/models.py
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Text
from .db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "student" | "professor"
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)      # comma-separated
    interests: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # comma-separated
    links: Mapped[Optional[str]] = mapped_column(Text, nullable=True)       # comma-separated URLs

    # relationships
    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r} role={self.role!r}>"

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # comma-separated
    stack: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # comma-separated (approved)

    owner: Mapped["User"] = relationship(back_populates="projects")

    def __repr__(self) -> str:
        return f"<Project id={self.id} title={self.title!r} owner_id={self.owner_id}>"

class StudentWatchlist(Base):
    """
    Optional: used by your 'Opportunity Scanner' agent.
    topics: comma-separated keywords
    cadence: "hourly" | "daily" | "weekly"
    """
    __tablename__ = "student_watchlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    topics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cadence: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<Watchlist id={self.id} user_id={self.user_id} cadence={self.cadence!r}>"
