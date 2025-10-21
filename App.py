# app.py
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="WellnessCoach",
    page_icon="💚",
    layout="centered",
)

# ---------- UI Header ----------
st.title("💚 WellnessCoach")
st.caption("Fitness • Meals • Sleep • Mindset — built for mobile.")

# ---------- Tiny rule-based brain (swap later for a real LLM) ----------
def coach_reply(text: str) -> str:
    t = text.lower().strip()

    # quick intent hints
    if any(k in t for k in ["truck", "lorry", "cab"]):
        return (
            "Here are **3 workouts you can do in your truck**:\n\n"
            "1) **Seat Push-ups** – Hands on door frame/dashboard, core tight, 3×15\n"
            "2) **Bodyweight Squats** – Feet shoulder width, slow tempo, 3×20\n"
            "3) **Seated Isometric Plank** – Brace core, push feet into floor, 3×30–45s\n\n"
            "Tip: keep a **light resistance band** in the cab for rows and face-pulls."
        )

    if any(k in t for k in ["meal", "diet", "calorie", "protein", "food", "eat"]):
        return (
            "Quick **3-meal template** you can use on the road:\n\n"
            "• **Breakfast:** Greek yogurt, granola, berries (≈450 kcal, 30–40g protein)\n"
            "• **Lunch:** Wholegrain wrap + chicken, salad, hummus (≈550 kcal, 35–45g protein)\n"
            "• **Dinner:** Ready rice + tinned tuna/salmon + steam-bag veg (≈600 kcal, 40g protein)\n\n"
            "Snack ideas: mixed nuts (small handful), apples, jerky, protein shake."
        )

    if any(k in t for k in ["sleep", "fatigue", "tired", "insomnia"]):
        return (
            "**Sleep reset for drivers:**\n"
            "• Aim for a **fixed shutdown window** (even if short)\n"
            "• Dark/quiet: eye mask + foam earplugs\n"
            "• Caffeine: none in the last **8 hours**\n"
            "• 10-minute wind-down: slow nasal breathing, phone on airplane mode\n"
            "• If you wake: don’t clock-watch; same slow breathing for 3–5 mins"
        )

    if any(k in t for k in ["mindset", "stress", "motivation", "focus"]):
        return (
            "**3-minute mindset primer:**\n"
            "1) 60s box breathing (4-4-4-4)\n"
            "2) Write 1 win from today (tiny is fine)\n"
            "3) Decide the single next action (≤5 min) — then do only that"
        )

    # default helpful nudge
    return (
        "Tell me your **goal** (fat loss, strength, energy, sleep), your schedule, "
        "and what equipment (if any) you have. I’ll give you a simple plan you can run today."
    )

# ---------- Conversation state ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey! I’m your Wellness Coach. What’s your goal today?"}
    ]

# render history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# quick starter prompts (mobile-friendly)
st.write("")
cols = st.columns(2)
with cols[0]:
    if st.button("Truck workouts"):
        user = "Give me 3 workouts I can do in my truck."
        st.session_state.messages.append({"role": "user", "content": user})
        with st.chat_message("user"):
            st.markdown(user)
        reply = coach_reply(user)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.stop()
with cols[1]:
    if st.button("3-meal day"):
        user = "Plan a simple 3-meal day for the road."
        st.session_state.messages.append({"role": "user", "content": user})
        with st.chat_message("user"):
            st.markdown(user)
        reply = coach_reply(user)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.stop()

# chat input
user_input = st.chat_input("Ask anything… e.g., '3-day plan I can do around 12-hour shifts'")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    reply = coach_reply(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# footer
st.markdown(
    "<div style='opacity:0.6; font-size:0.85rem; text-align:center; margin-top:1.5rem;'>"
    f"WellnessCoach • {datetime.now().strftime('%H:%M')}"
    "</div>",
    unsafe_allow_html=True,
)
