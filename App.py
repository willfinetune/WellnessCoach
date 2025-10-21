# App.py — WellnessCoach (AI-powered + profile + chat memory)
import os
from datetime import datetime
import streamlit as st

# --- OpenAI client (uses your Streamlit Secret) ---
# Make sure your Streamlit Secrets include:
# OPENAI_API_KEY = "sk-..."
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(
    page_title="WellnessCoach",
    page_icon="💚",
    layout="centered",
)

# ---------------- Profile (sidebar) ----------------
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
        p["sex"] = cols[1].selectbox("Sex", ["Prefer not to say","Female","Male","Intersex","Nonbinary"], index=["Prefer not to say","Female","Male","Intersex","Nonbinary"].index(p["sex"]))
        p["units"] = st.radio("Units", ["metric","imperial"], horizontal=True, index=0 if p["units"]=="metric" else 1)

        if p["units"] == "metric":
            p["height_cm"] = st.number_input("Height (cm)", min_value=120, max_value=230, value=p["height_cm"])
            p["weight_kg"] = st.number_input("Weight (kg)", min_value=35, max_value=250, value=p["weight_kg"])
        else:
            # store as metric internally
            feet = st.number_input("Height (feet)", min_value=4, max_value=7, value=5)
            inches = st.number_input("Height (inches)", min_value=0, max_value=11, value=9)
            p["height_cm"] = round((feet*12 + inches) * 2.54)
            pounds = st.number_input("Weight (lb)", min_value=80, max_value=550, value=176)
            p["weight_kg"] = round(pounds * 0.453592, 1)

        p["goal"] = st.selectbox(
            "Primary goal",
            ["Improve energy","Fat loss","Build muscle/strength","Better sleep","Stress/mood","General wellness"],
            index=["Improve energy","Fat loss","Build muscle/strength","Better sleep","Stress/mood","General wellness"].index(p["goal"])
        )
        p["equipment"] = st.text_input("Equipment available (e.g., dumbbells, band, gym, none)", value=p["equipment"])
        p["work_pattern"] = st.text_input("Schedule / work pattern", value=p["work_pattern"])
        p["diet_style"] = st.text_input("Diet style or constraints (e.g., halal, veggie, low-carb)", value=p["diet_style"])
        p["injuries"] = st.text_area("Injuries / limitations (optional)", value=p["injuries"])

        cols2 = st.columns(2)
        if cols2[0].button("Reset conversation"):
            st.session_state.messages = []
            st.rerun()
        cols2[1].button("Save profile")  # no-op, just persists in session

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
2) When planning workouts, adapt to equipment and time; include regressions if needed.
3) For nutrition, give simple meal ideas and portions, aligned to goal and diet style.
4) Include safety notes if injuries/limits are relevant.
5) Ask **one** follow-up question if useful to customize further.
6) Keep outputs brief but actionable on a phone.

Output in English. Keep units user-friendly (mention both if unclear).
"""

# ---------------- Chat memory ----------------
def init_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_reply" not in st.session_state:
        st.session_state.last_reply = ""

def ai_reply(user_text: str, profile: dict) -> str:
    msgs = [{"role":"system","content": system_prompt(profile)}]
    # append history
    msgs.extend(st.session_state.messages)
    msgs.append({"role":"user","content": user_text})

    # higher temperature for variety, but not nonsense
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs,
        temperature=0.9,
        top_p=0.95,
        max_tokens=700,
        presence_penalty=0.3,
        frequency_penalty=0.2,
    )
    return resp.choices[0].message.content.strip()

# ---------------- UI ----------------
init_profile()
init_chat()

st.title("💚 WellnessCoach")
st.caption("Fitness • Meals • Sleep • Mindset — tailored to your profile.")

profile_panel()

# On first visit, nudge the user
if not st.session_state.messages:
    st.info("Tell me your goal and constraints. I’ll build you a plan you can start today.")
    examples = st.container()
    colA, colB = st.columns(2)
    if colA.button("Boost energy at work"):
        prompt = "I need steady energy at work. 3 simple habits to start this week?"
        st.session_state.messages.append({"role":"user","content": prompt})
        reply = ai_reply(prompt, st.session_state.profile)
        st.session_state.messages.append({"role":"assistant","content": reply})
        st.rerun()
    if colB.button("30-min no-equipment plan"):
        prompt = "Make me a 30-minute, no-equipment workout I can do 3x/week."
        st.session_state.messages.append({"role":"user","content": prompt})
        reply = ai_reply(prompt, st.session_state.profile)
        st.session_state.messages.append({"role":"assistant","content": reply})
        st.rerun()

# show history
for m in st.session_state.messages:
    with st.chat_message("user" if m["role"]=="user" else "assistant"):
        st.markdown(m["content"])

# chat input
user_text = st.chat_input("Ask anything… e.g., '3-day plan around 12-hour shifts'")
if user_text:
    st.session_state.messages.append({"role":"user","content": user_text})
    with st.chat_message("assistant"):
        reply = ai_reply(user_text, st.session_state.profile)
        st.markdown(reply)
    st.session_state.messages.append({"role":"assistant","content": reply})
