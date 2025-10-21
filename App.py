# App.py — WellnessCoach (AI-powered + profile + chat memory)
# Requires: streamlit>=1.32, openai>=1.12, tiktoken>=0.5 (see requirements.txt)
# Secrets: set OPENAI_API_KEY in Streamlit Secrets

import os
from datetime import datetime
import streamlit as st

# ------------- OpenAI client (uses your Streamlit Secret) -------------
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --------------------------- Page config ------------------------------
st.set_page_config(
    page_title="WellnessCoach",
    page_icon="💚",
    layout="centered",
)

# ========================= Profile handling ===========================
def init_profile():
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "",
            "age": 30,
            "sex": "Prefer not to say",
            "height_cm": 175,
            "weight_kg": 80,
            "goal": "Improve energy",
            "equipment": "None",
            "work_pattern": "Day shift",
            "injuries": "",
            "diet_style": "No preference",
            "units": "metric",
        }

def profile_panel():
    p = st.session_state.profile
    with st.sidebar:
        st.header("Your profile")
        p["name"] = st.text_input("Name (optional)", value=p["name"])
        cols = st.columns(2)
        p["age"] = cols[0].number_input("Age", min_value=13, max_value=100, value=p["age"])
        sex_options = ["Prefer not to say", "Female", "Male", "Intersex", "Nonbinary"]
        p["sex"] = cols[1].selectbox("Sex", sex_options, index=sex_options.index(p["sex"]))
        p["units"] = st.radio("Units", ["metric", "imperial"], horizontal=True,
                              index=0 if p["units"] == "metric" else 1)

        if p["units"] == "metric":
            p["height_cm"] = st.number_input("Height (cm)", min_value=120, max_value=230, value=p["height_cm"])
            p["weight_kg"] = st.number_input("Weight (kg)", min_value=35, max_value=250, value=p["weight_kg"])
        else:
            # store internally as metric
            feet = st.number_input("Height (feet)", min_value=4, max_value=7, value=5)
            inches = st.number_input("Height (inches)", min_value=0, max_value=11, value=9)
            p["height_cm"] = round((feet * 12 + inches) * 2.54)
            pounds = st.number_input("Weight (lb)", min_value=80, max_value=550, value=176)
            p["weight_kg"] = round(pounds * 0.453592, 1)

        goals = ["Improve energy", "Fat loss", "Build muscle/strength", "Better sleep", "Stress/mood", "General wellness"]
        p["goal"] = st.selectbox("Primary goal", goals, index=goals.index(p["goal"]))
        p["equipment"] = st.text_input("Equipment (e.g., dumbbells, band, gym, none)", value=p["equipment"])
        p["work_pattern"] = st.text_input("Schedule / work pattern", value=p["work_pattern"])
        p["diet_style"] = st.text_input("Diet style or constraints (e.g., halal, veggie, low-carb)", value=p["diet_style"])
        p["injuries"] = st.text_area("Injuries / limitations (optional)", value=p["injuries"])

        cols2 = st.columns(2)
        if cols2[0].button("Reset conversation"):
            st.session_state.messages = []
            st.rerun()
        cols2[1].button("Save profile")  # persists in session

def system_prompt(profile: dict) -> str:
    """Build a targeted system prompt using the user's profile."""
    return f"""
You are **WellnessCoach**, a warm, practical, *mobile-first* health coach.
Communicate like a supportive human coach: concise, positive, and specific.
Vary your phrasing and structure so replies do not sound repetitive. Use bullets,
short paragraphs, and occasional emojis for warmth (not every message).

Personalize everything using this profile:
- Name: {profile.get('name') or 'Friend'}
- Age: {profile.get('age')}
- Sex: {profile.get('sex')}
- Height(cm): {profile.get('height_cm')}
- Weight(kg): {profile.get('weight_kg')}
- Goal: {profile.get('goal')}
- Schedule: {profile.get('work_pattern')}
- Equipment: {profile.get('equipment')}
- Diet style: {profile.get('diet_style')}
- Injuries/limits: {profile.get('injuries') or 'none'}

Coaching rules:
1) Give practical next steps the user can do *today*.
2) For workouts, adapt to equipment and time; include regressions if needed.
3) For nutrition, give simple meal ideas and portions aligned to goal & diet style.
4) Include safety notes if injuries/limits are relevant.
5) Ask **one** follow-up question if useful to customize further.
6) Keep outputs brief but actionable on a phone.

Output in English. If units are unclear, mention both metric and imperial.
"""

# ============================ Chat memory =============================
def init_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list[dict{role, content}]

def ai_reply(user_text: str, profile: dict) -> str:
    msgs = [{"role": "system", "content": system_prompt(profile)}]
    msgs.extend(st.session_state.messages)
    msgs.append({"role": "user", "content": user_text})

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs,
        temperature=0.9,      # variety without nonsense
        top_p=0.95,
        max_tokens=700,
        presence_penalty=0.3,
        frequency_penalty=0.2,
    )
    return resp.choices[0].message.content.strip()

# ================================ UI =================================
init_profile()
init_chat()

st.title("💚 WellnessCoach")
st.caption("Fitness • Meals • Sleep • Mindset — tailored to your profile.")

profile_panel()

# On first visit, nudge the user
if not st.session_state.messages:
    st.info("Tell me your goal and constraints. I’ll build you a plan you can start today.")
    examples = st.container()
else:
    examples = st.container()

# ---------- Example chips (optional, mobile-friendly) ----------
with examples:
    st.caption("Try one:")
    ex_cols = st.columns(3)
    if ex_cols[0].button("Truck workouts"):
        prompt = "Can you give me a short workout I can do in my truck with no equipment?"
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            reply = ai_reply(prompt, st.session_state.profile)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception:
            st.error("AI error — try again in a moment.")
        st.rerun()

    if ex_cols[1].button("3-meal day"):
        prompt = "Plan a simple 3-meal day for my goal with a small shopping list."
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            reply = ai_reply(prompt, st.session_state.profile)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception:
            st.error("AI error — try again soon.")
        st.rerun()

    if ex_cols[2].button("Better sleep"):
        prompt = "Give me a bedtime routine to improve sleep for my schedule."
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            reply = ai_reply(prompt, st.session_state.profile)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception:
            st.error("AI error — try again soon.")
        st.rerun()

# ---------- Render chat history as bubbles ----------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---------- Chat input ----------
user_text = st.chat_input("Ask anything… e.g., '3-day plan around 12-hour shifts'")
if user_text:
    # show + store user message
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # get AI reply
    try:
        reply = ai_reply(user_text, st.session_state.profile)
    except Exception:
        reply = "Sorry—something went wrong reaching the AI. Please try again."

    # show + store assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
