# app.py
import os
import re
import json
import time
from typing import Dict, Any, List, Optional

import requests
import streamlit as st

# -----------------------------
# Config
# -----------------------------
st.set_page_config(page_title="Campus Networking Chatbot", page_icon="🎓", layout="wide")
API_DEFAULT = os.getenv("BACKEND_URL", "http://localhost:8000")  # set BACKEND_URL env or edit here


# -----------------------------
# HTTP helpers (strict: no fallbacks)
# -----------------------------
def api_get(base: str, path: str, params: Dict[str, Any] | None = None) -> Any:
    url = f"{base}{path}"
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def api_post(base: str, path: str, payload: Dict[str, Any] | None = None) -> Any:
    url = f"{base}{path}"
    r = requests.post(url, json=payload or {}, timeout=20)
    r.raise_for_status()
    return r.json()


# -----------------------------
# Small utilities
# -----------------------------
def extract_kv(text: str, key: str) -> Optional[str]:
    """Extract 'key: value' (until newline). Case-insensitive."""
    m = re.search(rf"{key}\s*:\s*([^\n]+)", text, re.IGNORECASE)
    return m.group(1).strip() if m else None

def detect_intent(role: str, text: str) -> str:
    t = text.lower().strip()
    if role == "professor":
        if t.startswith("/post") or "create project" in t or t.startswith("project:"):
            return "post_project"
        if "/stack" in t or "suggest stack" in t or "tech stack" in t or "draft stack" in t:
            return "draft_stack"
        if "approve" in t:
            return "approve_stack"
        if t.startswith("/match") or "match students" in t or "find students" in t:
            return "match_project"
    else:  # student
        if t.startswith("/peers") or "find peers" in t or "connect" in t:
            return "find_peers"
    return "unknown"

def help_text(role: str) -> str:
    if role == "professor":
        return (
            "You can type freely, or use quick commands:\n"
            "- `/post` with `title:` and `description:` to create a project\n"
            "- `draft stack` or `/stack` to propose a tech stack for the latest project\n"
            "- `approve` to save the proposed stack\n"
            "- `/match` to show top 5 students (or `/match project_id: 12`)\n\n"
            "Example:\n"
            "```\n"
            "/post title: On-device SLAM for drones\n"
            "description: Build an object detection + SLAM pipeline on a low-power camera\n"
            "```"
        )
    return (
        "You can type freely, or use:\n"
        "- `/peers interests: computer vision, robotics  skills: Python, OpenCV`\n"
        "I’ll return top 5 peers to connect with."
    )


# -----------------------------
# Sidebar (backend + identity)
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    backend_url = st.text_input("Backend URL", value=API_DEFAULT, help="Your FastAPI base URL")
    role = st.radio("I am a...", options=["student", "professor"], index=0, horizontal=True)
    if role == "student":
        student_id = st.number_input("Your student user id", min_value=1, value=1, step=1)
    else:
        professor_id = st.number_input("Your professor user id", min_value=1, value=10, step=1)
        default_project_id = st.number_input("Default project id (for /match)", min_value=1, value=1, step=1)
    st.caption("All data loads from your backend. No local/demo data.")


# -----------------------------
# Session state
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"Hi! I'm your campus networking assistant.\n\n{help_text('student' if role=='student' else 'professor')}",
        }
    ]

if "ctx" not in st.session_state:
    st.session_state.ctx = {
        "last_project_id": None,
        "last_draft_stack": None,
    }


# -----------------------------
# UI: Chat transcript
# -----------------------------
st.title("🎓 Campus Networking — Chatbot")
st.write("Chat-first interface for students & professors.")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Type a message (use /help for commands)…")


# -----------------------------
# Message handling
# -----------------------------
def reply(text: str):
    st.session_state.messages.append({"role": "assistant", "content": text})
    with st.chat_message("assistant"):
        st.markdown(text)


if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if prompt.strip().lower() in ("/help", "help"):
        reply(help_text(role))
    else:
        try:
            intent = detect_intent(role, prompt)

            # -----------------------------
            # Professor flow
            # -----------------------------
            if role == "professor":
                if intent == "post_project":
                    title = extract_kv(prompt, "title") or "Untitled Project"
                    desc = extract_kv(prompt, "description") or prompt
                    payload = {
                        "owner_id": int(professor_id),
                        "title": title,
                        "description": desc,
                    }
                    proj = api_post(backend_url, "/projects", payload)
                    st.session_state.ctx["last_project_id"] = proj["id"]
                    reply(f"✅ Project created (id **{proj['id']}**): **{proj['title']}**\n\n{proj['description']}\n\nType `draft stack` to get a proposed tech stack.")

                elif intent == "draft_stack":
                    pid = st.session_state.ctx.get("last_project_id")
                    if not pid:
                        reply("I don't see a project yet. Use `/post title: ... description: ...` first.")
                    else:
                        out = api_post(backend_url, f"/projects/{pid}/draft_stack", {})
                        st.session_state.ctx["last_draft_stack"] = out
                        reply("🧠 Proposed tech stack:\n\n```json\n" + json.dumps(out, indent=2) + "\n```\nType **approve** to accept.")

                elif intent == "approve_stack":
                    pid = st.session_state.ctx.get("last_project_id")
                    draft = st.session_state.ctx.get("last_draft_stack")
                    if not pid or not draft:
                        reply("No draft stack to approve yet. Use `draft stack` first.")
                    else:
                        api_post(backend_url, "/projects/approve_stack", {"project_id": int(pid), "stack": draft["stack"]})
                        reply("✅ Stack approved and saved to the project.")

                elif intent == "match_project":
                    # Optional explicit project_id
                    pid_str = extract_kv(prompt, "project_id")
                    if pid_str is not None:
                        pid = int(pid_str)
                    else:
                        pid = st.session_state.ctx.get("last_project_id") or int(default_project_id)

                    reply(f"🔎 Matching students for project **{pid}**…")
                    time.sleep(0.2)
                    ranked = api_get(backend_url, f"/match/project/{pid}")
                    if not isinstance(ranked, list) or len(ranked) == 0:
                        reply("No matching students found.")
                    else:
                        lines = []
                        for i, s in enumerate(ranked[:5], 1):
                            lines.append(
                                f"**#{i}** — {s.get('name')} — {s.get('email')}  \n"
                                f"Skills: {s.get('skills','')}  \n"
                                f"Interests: {s.get('interests','')}"
                            )
                        reply("\n\n".join(lines))

                else:
                    reply("I didn't catch that.\n\n" + help_text("professor"))

            # -----------------------------
            # Student flow
            # -----------------------------
            else:
                if intent == "find_peers":
                    interests = extract_kv(prompt, "interests") or prompt
                    skills = extract_kv(prompt, "skills") or ""
                    peers = api_post(
                        backend_url,
                        "/match/peers",
                        {"user_id": int(student_id), "interests": interests, "skills": skills},
                    )
                    if not isinstance(peers, list) or len(peers) == 0:
                        reply("No peers found for those filters.")
                    else:
                        out = ["Here are your top peers:"]
                        for i, p in enumerate(peers[:5], 1):
                            out.append(
                                f"\n**#{i}**  \n"
                                f"**{p.get('name','User')}**  \n"
                                f"{p.get('email','')}  \n"
                                f"_{p.get('summary','')}_  \n"
                                f"**Skills:** {p.get('skills','')}  \n"
                                f"**Interests:** {p.get('interests','')}"
                            )
                        reply("\n".join(out))
                else:
                    reply("I didn't catch that.\n\n" + help_text("student"))

        except requests.HTTPError as http_err:
            reply(f"❌ Backend error:\n```\n{http_err}\n```\nCheck server logs.")
        except Exception as e:
            reply(f"❌ Request failed:\n```\n{e}\n```\nVerify BACKEND_URL and that your FastAPI app is running.")


# -----------------------------
# Footer
# -----------------------------
st.caption(
    "Connects only to your FastAPI backend (/profiles, /projects, /projects/{id}/draft_stack, "
    "/projects/approve_stack, /match/project/{id}, /match/peers). No local sample data."
)
