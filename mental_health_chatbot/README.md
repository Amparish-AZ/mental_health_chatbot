# Mental Health Support Chatbot (Local‑first Streamlit App)

> **Purpose:** A friendly, stigma‑free companion for young adults and students to track mood, practice quick coping skills (like breathing), and have supportive, empathetic conversations. It can *optionally* connect to a GPT model for richer replies, and it includes built‑in crisis detection and safety rails.

## Why this project?
- Anxiety and stress are common, but stigma and access barriers make help hard.
- This app provides **private, local-first** support that feels safe and approachable.
- It **does not replace therapy**—it gently encourages seeking professional help when needed.

## Core features (MVP)
1. **Supportive Chat**
   - Empathetic replies with supportive prompts and tips.
   - Optional GPT integration (if you set an API key) with a safety‑focused system prompt.
   - Always checks for crisis keywords and displays an in‑app safety banner.

2. **Daily Mood Tracking**
   - 1–5 scale + optional notes.
   - Progress chart over time to spot patterns.
   - Local SQLite database (no cloud by default).

3. **Breathing Exercise**
   - On‑screen guided breath cycle (inhale–hold–exhale) with timers.
   - Quick reset button for “in‑the‑moment” calm.

4. **Resources Panel**
   - General guidance to reach **local emergency services** and trusted contacts.
   - Country‑specific resource placeholders (customize in `app/resources.py`).

## Safety, ethics & privacy
- **Crisis detection:** Lightweight keyword scanning to surface a safety banner and urge immediate real‑world help.
- **Boundaries:** The chatbot never claims to diagnose, treat, or replace professional care.
- **Privacy:** Uses a local SQLite DB under `./data/mhc.db`. No network calls unless you explicitly enable GPT.
- **Consent:** First‑run message clarifies purpose, limits, and emergency guidance.
- **Customizable resources:** Edit `resources.py` to set accurate local hotline links/numbers for your region and user base.

## Architecture (MVP)
```
Streamlit UI  ──────────┐
                        │
 Empathy engine (local) ├─► Safety check (classify + banner)
     ↳ optional GPT     │
                        │
 SQLite storage (mood & chat logs) ─► charts & insights
 Breathing guide (timed prompts)     ─► UI loop
 Resources (localizable)
```
- **Tech:** Python 3.10+, Streamlit, SQLite, Pandas, Matplotlib
- **Files:**
  - `app/streamlit_app.py` – main UI
  - `app/empathy.py` – empathetic reply generator (+ optional GPT adapter)
  - `app/safety.py` – crisis detection logic
  - `app/storage.py` – SQLite helpers
  - `app/resources.py` – safety/help resources (edit me for your locale)
  - `app/prompts.py` – safety‑focused system prompt for GPT
  - `data/schema.sql` – table definitions
  - `.env.example` – environment variables template
  - `requirements.txt` – project deps

## Data model
- `users(user_id TEXT PRIMARY KEY, display_name TEXT, created_at TIMESTAMP)`
- `mood_logs(id INTEGER PK, user_id TEXT, date TEXT, mood INTEGER, note TEXT)`
- `chat_logs(id INTEGER PK, user_id TEXT, ts TIMESTAMP, role TEXT, content TEXT)`

## Getting started

### 1) Create a virtual environment & install
```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
*(If `pip` needs it: `python -m pip install --upgrade pip`)*

### 2) (Optional) Enable GPT
- Copy `.env.example` to `.env` and set your keys.
- This app ships with a **local empathetic engine**. If a valid key is present, it will use GPT instead.

### 3) Run the app
```bash
streamlit run app/streamlit_app.py
```
Streamlit will display a local URL (usually `http://localhost:8501`).

## Configuration
- **Environment variables** (via `.env`):
  - `OPENAI_API_KEY` (optional): Only used if you want GPT responses.
  - `OPENAI_MODEL` (optional): model name. Defaults to a small 4o‑mini‑style if present; otherwise local engine.
  - `COUNTRY_CODE` (optional): e.g., `IN`, `IE`, `DE` (affects the resources panel).

## Demo flows

### 1) Daily check‑in
1. User sets Display Name in sidebar.
2. Selects today’s mood (1–5) and adds a short note.
3. Sees 14‑day mood chart update immediately.

### 2) In‑the‑moment support
1. User types “I have an exam tomorrow and I’m spiraling.”
2. Bot responds with empathy, asks permission to suggest a skill.
3. User clicks **Start breathing** → guided inhale–hold–exhale cycle.

### 3) Crisis safeguard
1. User types “I want to end it.”
2. App displays a **red safety banner** with urgent guidance to contact local emergency services, and the reply prioritizes safety language and grounding steps (no treatment claims).

## Roadmap (post‑MVP)
- Journaling & gratitude prompts (with tags).
- Emotion labeling & trigger tracking.
- CBT‑inspired reframing tool (with opt‑in privacy).
- Multi‑user auth & export of personal data.
- Long‑term trends (weekly/monthly aggregates).

## License
MIT – do anything with attribution and no liability. See `LICENSE`.

---

### Important disclaimers
- This tool is **not** medical advice or a substitute for therapy. If you’re in danger or considering harming yourself or others, **contact your local emergency number immediately** (e.g., *112 in India, 999 in the UK, 911 in the US*) or go to the nearest emergency department.
- Always verify and update the **Resources** list for your region before deploying to users.
