# app/safety.py
from __future__ import annotations
import re
from dataclasses import dataclass

CRISIS_PATTERNS = [
    r"kill myself", r"end my life", r"suicide", r"die by suicide",
    r"i don\'t want to live", r"hurt myself", r"self[- ]harm",
    r"cutting myself", r"overdose", r"harm others", r"kill (him|her|them)",
]

CRISIS_RE = re.compile("|".join(CRISIS_PATTERNS), re.IGNORECASE)

@dataclass
class SafetyAssessment:
    risk: str  # "none", "concern", "crisis"
    reason: str | None = None

def assess_risk(text: str) -> SafetyAssessment:
    if not text:
        return SafetyAssessment("none")
    if CRISIS_RE.search(text):
        return SafetyAssessment(risk="crisis", reason="Matched crisis keywords")
    # If extreme despair language, flag concern (so the bot slows down and checks in)
    if any(w in text.lower() for w in ["hopeless", "worthless", "can't cope", "overwhelmed"]):
        return SafetyAssessment(risk="concern", reason="Detected intense distress terms")
    return SafetyAssessment("none")
