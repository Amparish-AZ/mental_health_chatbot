# app/streamlit_app.py
from __future__ import annotations

# ---------- imports & setup ----------
from pathlib import Path
import sys, os, time, uuid, datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv

# Ensure package imports work when running as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # .../mental_health_chatbot
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# --- must be the FIRST Streamlit command ---
st.set_page_config(page_title="Mental Health Support Chatbot", page_icon="🫶", layout="centered")
# -------------------------------------------

load_dotenv()

from app import storage, safety, empathy, resources

# ---------- one-time init ----------
storage.init_db()

# Session defaults
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "display_name" not in st.session_state:
    st.session_state.display_name = ""
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_engine" not in st.session_state:
    st.session_state.last_engine = "-"
if "last_error" not in st.session_state:
    st.session_state.last_error = ""

# Show current reply mode + last engine actually used
mode = "GPT" if os.getenv("OPENAI_API_KEY") else "Local"
st.sidebar.caption(f"Reply mode: **{mode}** | Model: **{os.getenv('OPENAI_MODEL','(default)')}**")
st.sidebar.caption(f"Last reply engine: **{st.session_state.last_engine}**")
if st.session_state.last_error:
    st.sidebar.warning(f"Last GPT error: {st.session_state.last_error}")

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("## Settings")
    st.session_state.display_name = st.text_input(
        "Display name (optional):",
        value=st.session_state.display_name,
        placeholder="e.g., Sam"
    )
    storage.upsert_user(st.session_state.user_id, st.session_state.display_name or None)

    st.markdown("---")
    st.markdown("### Breathing exercise")
    inhale = st.number_input("Inhale (sec)", min_value=3, max_value=10, value=4, step=1)
    hold = st.number_input("Hold (sec)", min_value=0, max_value=10, value=2, step=1)
    exhale = st.number_input("Exhale (sec)", min_value=4, max_value=12, value=6, step=1)
    cycles = st.number_input("Cycles", min_value=1, max_value=8, value=3, step=1)
    if st.button("Start breathing"):
        placeholder = st.empty()
        for c in range(int(cycles)):
            placeholder.info(f"Cycle {c+1}/{int(cycles)} – Inhale")
            time.sleep(int(inhale))
            if hold:
                placeholder.warning("Hold")
                time.sleep(int(hold))
            placeholder.success("Exhale")
            time.sleep(int(exhale))
        placeholder.empty()
        st.success("Nice job. Notice what changed in your body, even a little.")

    st.markdown("---")
    st.markdown("### Resources")
    cc = os.getenv("COUNTRY_CODE", "IN")
    for line in resources.emergency_lines(cc):
        st.markdown(f"- {line}")

# ---------- main ----------
st.title("🫶 Mental Health Support")
st.caption("A gentle space to check in, practice a quick skill, and talk things through. Not a substitute for therapy.")

# --- Mood tracker ---
st.subheader("Daily mood check-in")
today = dt.date.today().isoformat()
mood = st.slider("How are you feeling today?", min_value=1, max_value=5, value=3, format="%d")
note = st.text_input("Add a short note (optional):", placeholder="e.g., exam stress, slept well, met a friend")
if st.button("Save today’s mood"):
    storage.log_mood(st.session_state.user_id, today, int(mood), note.strip() or None)
    st.success("Saved. Be kind to yourself today.")

series = storage.fetch_mood_series(st.session_state.user_id, limit_days=14)
if series:
    dates = [d for d, _ in series]
    vals = [v for _, v in series]
    fig, ax = plt.subplots()
    ax.plot(dates, vals, marker="o")
    ax.set_ylim(1, 5)
    ax.set_ylabel("Mood (1–5)")
    ax.set_xlabel("Date")
    ax.set_title("Last 14 days")
    st.pyplot(fig)

st.markdown("---")

# --- Supportive chat ---
st.subheader("Supportive chat")
st.caption("The assistant listens, validates, and offers simple coping ideas. If a crisis is detected, we’ll show a safety banner.")

# Show history
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_msg = st.chat_input("Type how you’re feeling...")
if user_msg:
    # Log + show user message
    st.session_state.chat.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)
    storage.log_chat(st.session_state.user_id, "user", user_msg)

    # Safety check
    assess = safety.assess_risk(user_msg)
    if assess.risk == "crisis":
        st.error(
            "🚨 You matter. If you’re in immediate danger or thinking about harming yourself or others, "
            "call your local emergency number now (e.g., 112 in India, 999 in the UK, 911 in the US) or go to the nearest emergency department. "
            "Consider telling a trusted person nearby."
        )

    # Generate reply (returns text + engine + debug)
    msgs = [{"role": "user", "content": user_msg}]
    bot_text, engine, dbg = empathy.generate_reply(msgs)
    st.session_state.last_engine = engine
    st.session_state.last_error = dbg

    with st.chat_message("assistant"):
        st.markdown(bot_text)
    st.session_state.chat.append({"role": "assistant", "content": bot_text})
    storage.log_chat(st.session_state.user_id, "assistant", bot_text)

st.markdown("---")
st.caption("**Disclaimer:** This tool does not provide medical advice and isn’t a replacement for professional care.")
