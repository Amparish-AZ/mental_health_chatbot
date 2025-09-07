# app/empathy.py
from __future__ import annotations
import os, random
from typing import List, Dict, Tuple
from .prompts import SYSTEM_PROMPT

def _local_empathy_engine(messages: List[Dict[str, str]]) -> str:
    openers = [
        "Thanks for sharing that. I hear how tough this feels.",
        "I’m really glad you told me — that took courage.",
        "I hear you. That sounds heavy to carry.",
    ]
    suggestions = [
        "Would a quick 1–2 minute breathing reset help right now?",
        "We can try a tiny next step, like writing down one worry and one thing you can control.",
        "If you like, I can share a grounding exercise that uses the five senses.",
    ]
    questions = [
        "What would feel most supportive in this moment?",
        "Do you want to talk it through, try a skill, or both?",
        "What’s one small thing that might ease this by 5%?",
    ]
    return f"{random.choice(openers)} {random.choice(suggestions)} {random.choice(questions)}"

def _openai_client():
    try:
        from openai import OpenAI  # SDK v1.x
    except Exception as e:
        return None, f"openai SDK import failed: {e}"
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, "OPENAI_API_KEY not set"
    try:
        return OpenAI(api_key=api_key), None
    except Exception as e:
        return None, f"OpenAI client init failed: {e}"

def _extract_responses_text(resp) -> str:
    """Flatten text from the Responses API output."""
    parts = []
    if not getattr(resp, "output", None):
        return ""
    for item in resp.output:
        for seg in getattr(item, "content", []) or []:
            txt = getattr(seg, "text", None)
            if txt:
                parts.append(txt)
    return " ".join(parts).strip()

def generate_reply(messages: List[Dict[str, str]]) -> Tuple[str, str, str]:
    """
    Returns (text, engine, debug). engine is 'gpt' or 'local'.
    debug has the last error if any.
    """
    client, init_err = _openai_client()
    if client is None:
        return _local_empathy_engine(messages), "local", init_err or "no-client"

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    # 1) Try the Responses API (works with 4o/4o-mini/others)
    try:
        resp = client.responses.create(
            model=model,
            input=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            temperature=0.7,
            max_output_tokens=220,
        )
        txt = _extract_responses_text(resp)
        if txt:
            return txt, "gpt", ""
        raise ValueError("Responses API returned empty text")
    except Exception as e1:
        last_err = f"responses.create: {type(e1).__name__}: {e1}"

    # 2) Fallback to Chat Completions API
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            temperature=0.7,
            max_tokens=220,
        )
        txt = (resp.choices[0].message.content or "").strip()
        if txt:
            return txt, "gpt", f"(responses failed; used chat.completions)"
        raise ValueError("Chat Completions returned empty text")
    except Exception as e2:
        last_err = f"{last_err} | chat.completions.create: {type(e2).__name__}: {e2}"

    # 3) Final fallback: local engine
    return _local_empathy_engine(messages), "local", last_err
