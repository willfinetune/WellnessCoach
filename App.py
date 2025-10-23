# App.py — WellnessCoach (AI-powered + PWA + chat memory)
import os
from datetime import datetime
import streamlit as st
from openai import OpenAI

# --- OpenAI client (uses your Streamlit Secret) ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(
    page_title="WellnessCoach",
    page_icon="💚",
    layout="centered",
)

# --- PWA hooks: manifest + service worker registration ---
st.markdown(
    """
    <link rel="manifest" href="/static/manifest.webmanifest">
    <link rel="apple-touch-icon" href="/static/file_000000001e8c62439bd32306d8c7ab28.png">
    <meta name="theme-color" content="#43C67E">
    <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/service-worker.js').catch(function(e){
          console.log('SW reg failed', e);
        });
      });
    }
    </script>
    """,
    unsafe_allow_html=True,
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
        cols2[1].button("Save profile")

def system_prompt(profile: dict) -> str:
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

Output in English.
"""

# ---------------- Chat memory ----------------
def init_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_reply" not in st.session_state:
        st.session_state.last_reply = ""

def ai_reply(user_text: str, profile: dict) -> str:
    msgs = [{"role":"system","content": system_prompt(profile)}]
    msgs.extend(st.session_state.messages)
    msgs.append({"role":"user","content": user_text})

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

if not st.session_state.messages:
    st.info("Tell me your goal and constraints. I’ll build you a plan you can start today.")
    examples = st.container()
    with examples:
        st.markdown("Examples:")
        st.markdown("- ‘I drive a lorry 12 hours a day, I need energy tips.’")
        st.markdown("- ‘I’ve got dumbbells and want to lose fat.’")
        st.markdown("- ‘I sit all day and can’t sleep well.’")

prompt = st.chat_input("Ask anything... e.g., '3-day plan around 12-hour shifts'")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply = ai_reply(prompt, st.session_state.profile)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.last_reply = reply

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])
# --- iPhone Install Popup (appears only on iOS Safari) ---
st.markdown("""
    <script>
    const ua = window.navigator.userAgent;
    const isiOS = /iPad|iPhone|iPod/.test(ua);
    const isInStandalone = window.matchMedia('(display-mode: standalone)').matches;

    if (isiOS && !isInStandalone) {
        const banner = document.createElement('div');
        banner.style.position = 'fixed';
        banner.style.bottom = '0';
        banner.style.left = '0';
        banner.style.right = '0';
        banner.style.background = '#198754';
        banner.style.color = 'white';
        banner.style.padding = '14px';
        banner.style.textAlign = 'center';
        banner.style.fontSize = '15px';
        banner.style.zIndex = '9999';
        banner.style.fontFamily = 'sans-serif';
        banner.style.boxShadow = '0 -2px 8px rgba(0,0,0,0.25)';
        banner.innerHTML = '📱 <b>iPhone user?</b> Tap <img src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Share_iOS.png" width="16" style="vertical-align:middle;"> then <b>Add to Home Screen</b> to install <b>WellnessCoach</b>!';
        document.body.appendChild(banner);
    }
    </script>
""", unsafe_allow_html=True)
