# backend/seed.py
"""
Run from the project root:
    python -m backend.seed
Requires:
    - backend/__init__.py exists
    - DATABASE_URL set (or db.py defaults to SQLite)
"""
from backend.db import Base, engine, SessionLocal
from backend.models import User, Project, StudentWatchlist

def main():
    # Re-create schema (DANGEROUS in prod)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Professors
        prof = User(
            name="Prof. Diaz",
            role="professor",
            email="diaz@uni.edu",
            summary="Robotics & perception lab",
            skills="",
            interests=""
        )

        # Students
        s1 = User(
            name="Asha R.",
            role="student",
            email="asha@uni.edu",
            summary="CS MS, vision + RL",
            skills="Python, PyTorch, OpenCV, RL",
            interests="computer vision, robotics"
        )
        s2 = User(
            name="Ben K.",
            role="student",
            email="ben@uni.edu",
            summary="Full-stack dev",
            skills="React, TypeScript, Node, SQL",
            interests="web apps, edtech"
        )
        s3 = User(
            name="Chen L.",
            role="student",
            email="chen@uni.edu",
            summary="NLP + LLM tooling",
            skills="Python, LangChain, RAG, FastAPI",
            interests="chatbots, retrieval"
        )

        db.add_all([prof, s1, s2, s3])
        db.commit()
        db.refresh(prof); db.refresh(s1); db.refresh(s2); db.refresh(s3)

        # One example project
        proj = Project(
            owner_id=prof.id,
            title="Perception for Mobile Robot",
            description="Build a pipeline for on-device object detection and SLAM with a low-power camera.",
            tags="vision, robotics, embedded"
        )
        db.add(proj)
        db.commit()

        # Optional student watchlist rows
        w1 = StudentWatchlist(user_id=s1.id, topics="computer vision, robotics, SLAM", cadence="daily")
        w2 = StudentWatchlist(user_id=s3.id, topics="chatbots, LLM tools, retrieval", cadence="weekly")
        db.add_all([w1, w2])
        db.commit()

        print("✅ Seeded database successfully.")
        print(f"Professor id: {prof.id}")
        print(f"Student ids: {s1.id}, {s2.id}, {s3.id}")
        print(f"Project id: {proj.id}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
