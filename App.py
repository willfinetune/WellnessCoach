# app.py — WellnessCoach (mobile-first)
import streamlit as st
from datetime import datetime
import math, random

st.set_page_config(
    page_title="WellnessCoach",
    page_icon="💚",
    layout="centered",
)

# ---------- tiny helpers ----------
def v(options):  # random variant
    return random.choice(options)

def activity_factor(level):
    return {
        "Sedentary (little/no exercise)": 1.2,
        "Light (1–3 days/wk)": 1.375,
        "Moderate (3–5 days/wk)": 1.55,
        "Active (6–7 days/wk)": 1.725,
        "Very active (manual work/athlete)": 1.9,
    }[level]

def bmr(sex, kg, cm, age):
    # Mifflin–St Jeor
    base = 10*kg + 6.25*cm - 5*age
    return base + (5 if sex == "Male" else -161)

def tdee(sex, kg, cm, age, level):
    return round(bmr(sex, kg, cm, age) * activity_factor(level))

def kcal_target(tdee_val, goal):
    if goal == "Fat loss":
        return round(tdee_val * 0.8)  # ~20% deficit
    if goal == "Muscle gain":
        return round(tdee_val * 1.1)  # ~10% surplus
    return tdee_val  # Energy/Health/Maintenance

def bmi(kg, cm):
    return round(kg / (cm/100)**2, 1)

def bmi_label(b):
    if b < 18.5: return "Underweight"
    if b < 25:   return "Healthy"
    if b < 30:   return "Overweight"
    return "Obesity"

def protein_grams(kg, goal):
    # simple range by goal
    lo = 1.6 if goal == "Fat loss" else 1.8
    hi = 2.2 if goal == "Muscle gain" else 2.0
    return (round(kg*lo), round(kg*hi))

def ensure_profile():
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "",
            "sex": "Male",
            "age": 30,
            "height_cm": 175,
            "weight_kg": 75.0,
            "activity": "Moderate (3–5 days/wk)",
            "goal": "Energy/Health",
            "equipment": [],
        }

ensure_profile()
p = st.session_state.profile

# ---------- UI ----------
st.title("💚 WellnessCoach")
st.caption("Fitness • Meals • Sleep • Mindset — built for mobile.")

with st.expander("👤 Set up or edit your profile", expanded=True if not p["name"] else False):
    with st.form("profile_form", clear_on_submit=False):
        p["name"] = st.text_input("Name (optional)", value=p["name"], placeholder="e.g., Will")
        col1, col2 = st.columns(2)
        with col1:
            p["sex"] = st.selectbox("Sex", ["Male", "Female"], index=0 if p["sex"]=="Male" else 1)
            p["age"] = st.number_input("Age", 14, 90, value=int(p["age"]))
            p["height_cm"] = st.number_input("Height (cm)", 130, 220, value=int(p["height_cm"]))
        with col2:
            p["weight_kg"] = st.number_input("Weight (kg)", 35.0, 250.0, value=float(p["weight_kg"]), step=0.5)
            p["activity"] = st.selectbox(
                "Activity",
                [
                    "Sedentary (little/no exercise)",
                    "Light (1–3 days/wk)",
                    "Moderate (3–5 days/wk)",
                    "Active (6–7 days/wk)",
                    "Very active (manual work/athlete)",
                ],
                index=[
                    "Sedentary (little/no exercise)",
                    "Light (1–3 days/wk)",
                    "Moderate (3–5 days/wk)",
                    "Active (6–7 days/wk)",
                    "Very active (manual work/athlete)",
                ].index(p["activity"])
            )
            p["goal"] = st.selectbox("Primary goal", ["Fat loss","Muscle gain","Energy/Health"], index=["Fat loss","Muscle gain","Energy/Health"].index(p["goal"]))
        p["equipment"] = st.multiselect(
            "Equipment you can use (choose any)",
            ["Bodyweight only","Resistance band","Dumbbells","Kettlebell","Gym access"],
            default=p["equipment"] if p["equipment"] else ["Bodyweight only"]
        )
        submitted = st.form_submit_button("Save profile")
        if submitted:
            st.success(v(["Saved! ✅","Profile updated. 👍","Got it — thanks! 🙌"]))

# Stats bar
if p["height_cm"] and p["weight_kg"]:
    _bmi = bmi(p["weight_kg"], p["height_cm"])
    _tdee = tdee(p["sex"], p["weight_kg"], p["height_cm"], p["age"], p["activity"])
    _target = kcal_target(_tdee, p["goal"])
    pr_lo, pr_hi = protein_grams(p["weight_kg"], p["goal"])
    st.markdown(
        f"""
**Stats**  
• **BMI:** {_bmi} ({bmi_label(_bmi)})  
• **TDEE:** {_tdee} kcal/day  
• **Target:** {_target} kcal/day ({p['goal']})  
• **Protein:** {pr_lo}–{pr_hi} g/day
"""
    )

st.divider()

# ---------- Coaching logic ----------
def workouts_for_profile(days=3):
    eq = p["equipment"] or ["Bodyweight only"]
    has_band = "Resistance band" in eq
    has_db = "Dumbbells" in eq or "Kettlebell" in eq
    has_gym = "Gym access" in eq

    plan = []
    if days == 3:
        # Day 1: Push
        plan.append({
            "title": v(["Day 1 — Push","Day 1 — Upper (push)","Day 1 — Chest/Shoulders"]),
            "items": [
                ("Incline Push-ups (bench/cab/door frame)", "3×10–15"),
                ("Pike Push-ups or Shoulder Press" + (" (DB)" if has_db or has_gym else ""), "3×8–12"),
                ("Dips between seats" if not has_gym else "Machine/Bench Dips", "3×8–12"),
                (("Band Chest Fly" if has_band else "Push-up Hold (isometric)"), "3×30–45s"),
            ]
        })
        # Day 2: Legs & Core
        plan.append({
            "title": v(["Day 2 — Legs & Core","Day 2 — Lower body + core"]),
            "items": [
                ("Squats" + (" (DB goblet)" if has_db else ""), "4×10–15"),
                ("Reverse Lunges", "3×8–12/leg"),
                ("Romanian Deadlift" + (" (DB/band)" if has_db or has_band else " (hip hinge)"), "3×10–12"),
                ("Plank variations", "3×30–60s"),
            ]
        })
        # Day 3: Pull & Conditioning
        plan.append({
            "title": v(["Day 3 — Pull & Conditioning","Day 3 — Back + cardio"]),
            "items": [
                (("Band Rows" if has_band else "Back Pack Rows"), "4×10–15"),
                ("Face-pulls (band) or Rear-delt raises (DB)", "3×12–15"),
                ("Farmer Carry (DBs or heavy bag)", "5×40–60m"),
                ("10–15 min brisk walk / stairs / shadow boxing", "Easy pace"),
            ]
        })
    else:
        plan.append({"title":"Full-body (short)","items":[("Squat","3×15"),("Push-up","3×12"),("Row/Band Row","3×15"),("Plank","3×45s")]})
    return plan

def sample_meals(kcal, protein_range):
    # crude split; keeps variety by cycling options
    pr = random.randint(*protein_range)
    carbs = round(kcal * 0.45 / 4)
    fat_g = round(kcal * 0.25 / 9)

    breakfast = v([
        "Greek yogurt bowl + oats, berries, honey, and seeds",
        "3 eggs + toast + avocado + tomato",
        "Protein smoothie (milk, whey, banana, oats, PB)"
    ])
    lunch = v([
        "Chicken wrap with veggies + hummus",
        "Tuna & rice bowl with sweetcorn and olive oil",
        "Lentil & feta salad with whole-grain pita"
    ])
    dinner = v([
        "Stir-fry beef/chicken + veg + noodles/rice",
        "Salmon, potatoes, and greens",
        "Chili (lean mince/beans) with rice"
    ])
    snacks = v([
        "Mixed nuts + fruit",
        "Cottage cheese + crackers",
        "Protein bar + apple",
        "Carrots & hummus + yogurt"
    ])
    return pr, carbs, fat_g, breakfast, lunch, dinner, snacks

def coach_reply(text: str):
    text_l = text.lower().strip()
    greeting = v([
        "Got you.", "Nice — let’s do it.", "Sweet, here’s a plan.", "Alright, coach mode on."
    ])

    if any(k in text_l for k in ["truck", "lorry"]):
        intro = v([
            "Road-friendly ideas you can do in/around the cab:",
            "Driver-fit routine you can run anywhere:",
            "No-gym trucker plan:"
        ])
        lines = [
            "• **Seat Push-ups** – hands on door frame/dashboard, core tight (3×12–15)",
            "• **Box Squats** to seat edge (4×12)",
            "• **Isometric Plank (seated)** – brace core, push feet into floor (3×40s)",
            "• **Band Rows/Face-pulls** if you carry a band (3×15)",
            "• Finish with 10–12 min brisk walk at stops"
        ]
        return greeting + " " + intro + "\n" + "\n".join(lines)

    # workout request
    if "workout" in text_l or "plan" in text_l and any(k in text_l for k in ["day","push","pull","legs","full"]):
        days = 3 if "3" in text_l else 2 if "2" in text_l else 3
        plan = workouts_for_profile(days)
        out = [greeting, v(["Here’s a structured split:", "Try this schedule:", "This will work well for you:"])]
        for d in plan:
            out.append(f"\n**{d['title']}**")
            for name, reps in d["items"]:
                out.append(f"- {name} — {reps}")
        out.append("\nTip: keep 1–2 reps in reserve; log sets to progress.")
        return "\n".join(out)

    # meals / calories
    if any(k in text_l for k in ["meal","calorie","calories","food","diet"]):
        _tdee = tdee(p["sex"], p["weight_kg"], p["height_cm"], p["age"], p["activity"])
        target = kcal_target(_tdee, p["goal"])
        pr, carbs, fat_g, b,l,d,sn = sample_meals(target, protein_grams(p["weight_kg"], p["goal"]))
        return (
            f"{greeting} Based on your profile, aim for **~{target} kcal/day**.\n"
            f"- Protein: **{pr} g** • Carbs: **~{carbs} g** • Fat: **~{fat_g} g**\n\n"
            f"**Example day**\n"
            f"- Breakfast: {b}\n- Lunch: {l}\n- Dinner: {d}\n- Snack: {sn}\n\n"
            f"{v(['Swap any protein/carb/fat like-for-like to keep the calories steady.',
                'Keep fiber high and water handy, especially on busy days.',
                'Batch-cook once and eat twice to save time.'])}"
        )

    # default guidance
    tips = [
        "Log 7–8k steps/day as baseline.",
        "2–3 strength sessions/week drive results.",
        "Protein at 3–4 meals keeps you full.",
        "Sleep: 7–9h if you can."
    ]
    return greeting + " " + v([
        "Tell me your exact goal and time you can train; I’ll lay out a simple week.",
        "Share your schedule and what equipment you can use; I’ll tailor it.",
        "Say “meal plan” or “workout plan” to get a precise template."
    ]) + "\n\nQuick wins: " + " · ".join(random.sample(tips, k=3))

# ---------- Chat UI ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# seed message (varied)
if not st.session_state.messages:
    seed = v([
        "What’s your goal this month — fat loss, muscle, or energy?",
        "Want a workout or a day of meals? Tell me your goal and schedule.",
        "Tell me your goal + equipment and I’ll build a plan."
    ])
    st.session_state.messages.append({"role":"assistant","content": seed})

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask anything… e.g., '3-day plan I can do around 12-hour shifts'")
if prompt:
    st.session_state.messages.append({"role":"user","content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = coach_reply(prompt)
    st.session_state.messages.append({"role":"assistant","content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# footer
st.caption("This app provides general education — not medical advice. If you have a condition, consult a professional.")
