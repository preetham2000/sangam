import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import profiles, projects, match

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Campus Networking Backend")

# CORS for local dev + Streamlit
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8501",  # Streamlit default
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(projects.router)
app.include_router(match.router)

@app.get("/")
def root():
    return {"ok": True}
