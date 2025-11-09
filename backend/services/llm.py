import os, json
from typing import Dict, Any
from openai import OpenAI
from pydantic import ValidationError
from ..schemas import StackDraft
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set. Add it to your .env file.")
client = OpenAI(api_key=OPENAI_API_KEY)

STACK_PROMPT = """You are a precise assistant. A professor described a project.
Return STRICT JSON with keys exactly: stack (3-6 items), skills (2-4 items), evaluation (1-2 items).
No extra commentary.

Project:
"""

def draft_stack_for_project(description: str) -> Dict[str, Any]:
    msg = STACK_PROMPT + description
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Return only strict JSON. No prose."},
            {"role": "user", "content": msg},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    data = json.loads(raw)
    try:
        StackDraft(**data)  # validate shape
    except ValidationError as e:
        raise ValueError(f"LLM JSON did not validate: {e}")
    return data
