import streamlit as st
from datetime import date

# -----------------------------
# Page config (moet bovenaan!)
# -----------------------------
st.set_page_config(
    page_title="TripBuilder",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Minimal "data model" in session_state
# -----------------------------
def init_state():
    if "trip" not in st.session_state:
        st.session_state.trip = {
            "destination": "Barcelona",
            "start_date": date.today(),
            "end_date": date.today(),
            "budget_eur": 800,
            "travelers": 1,
            "interests": ["Food", "Culture"],
            "notes": "",
        }

    if "draft_items" not in st.session_state:
        st.session_state.draft_items = []  # later gebruiken we dit in Itinerary

    if "ui" not in st.session_state:
        st.session_state.ui = {
            "show_tips": True,
            "last_saved": None,
        }


init_state()

# -----------------------------
# Styling (subtiel "nuts")
# -----------------------------
st.markdown(
    """
    <style>
      .tb-hero {
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        background: linear-gradient(120deg, rgba(0, 255, 180, 0.10), rgba(80, 120, 255, 0.10));
        border: 1px solid rgba(255,255,255,0.08);
      }
      .tb-kpi {
        padding: 0.9rem 1rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.03);
      }
      .tb-small {
        opacity: 0.85;
        font-size: 0.92rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Header / Hero
# -----------------------------
st.markdown(
    f"""
    <div class="tb-hero">
      <h1 style="margin:0;">🧭 TripBuilder</h1>
      <p class="tb-small" style="margin:0.25rem 0 0 0;">
        Plan je reis alsof je een film regisseert: budget, route, activiteiten, stats.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# -----------------------------
# Sidebar controls (globaal)
# -----------------------------
with st.sidebar:
    st.header("⚙️ Quick Controls")

    st.caption("Deze instellingen gelden overal (alle pagina’s).")

    # Quick edit essentials (globale inputs)
    st.session_state.trip["destination"] = st.text_input(
        "Bestemming",
        value=st.session_state.trip["destination"],
    )

    c1, c2 = st.columns(2)
    with c1:
        st.session_state.trip["start_date"] = st.date_input(
            "Start",
            value=st.session_state.trip["start_date"],
        )
    with c2:
        st.session_state.trip["end_date"] = st.date_input(
            "Einde",
            value=st.session_state.trip["end_date"],
        )

    st.session_state.trip["travelers"] = st.number_input(
        "Reizigers",
        min_value=1,
        max_value=20,
        value=int(st.session_state.trip["travelers"]),
        step=1,
    )

    st.session_state.trip["budget_eur"] = st.slider(
        "Budget (€)",
        min_value=0,
        max_value=10000,
        value=int(st.session_state.trip["budget_eur"]),
        step=50,
    )

    st.session_state.ui["show_tips"] = st.toggle(
        "Tips tonen",
        value=st.session_state.ui["show_tips"],
    )

    st.divider()

    # Quick actions
    a1, a2 = st.columns(2)
    with a1:
        if st.button("🧹 Reset trip"):
            st.session_state.trip = {
                "destination": "",
                "start_date": date.today(),
                "end_date": date.today(),
                "budget_eur": 0,
                "travelers": 1,
                "interests": [],
                "notes": "",
            }
            st.session_state.draft_items = []
            st.session_state.ui["last_saved"] = None
            st.rerun()

    with a2:
        if st.button("✨ Demo data"):
            st.session_state.trip["destination"] = "Tokyo"
            st.session_state.trip["budget_eur"] = 1800
            st.session_state.trip["travelers"] = 2
            st.session_state.trip["interests"] = ["Food", "Tech", "Culture"]
            st.session_state.draft_items = [
                {"day": 1, "time": "10:00", "title": "Senso-ji Temple", "cost": 0},
                {"day": 1, "time": "13:00", "title": "Ramen lunch", "cost": 25},
                {"day": 2, "time": "09:00", "title": "Akihabara walk", "cost": 0},
            ]
            st.rerun()

    st.caption("Tip: de echte pagina’s staan in de map `pages/`.")

# -----------------------------
# Main overview (landing)
# -----------------------------
trip = st.session_state.trip

colA, colB, colC, colD = st.columns(4)

with colA:
    st.markdown('<div class="tb-kpi">', unsafe_allow_html=True)
    st.metric("📍 Bestemming", trip["destination"] or "—")
    st.markdown("</div>", unsafe_allow_html=True)

with colB:
    days = (trip["end_date"] - trip["start_date"]).days + 1
    if days < 1:
        days = 0
    st.markdown('<div class="tb-kpi">', unsafe_allow_html=True)
    st.metric("🗓️ Duur", f"{days} dagen")
    st.markdown("</div>", unsafe_allow_html=True)

with colC:
    per_person = 0
    if trip["travelers"] > 0:
        per_person = int(trip["budget_eur"] / trip["travelers"])
    st.markdown('<div class="tb-kpi">', unsafe_allow_html=True)
    st.metric("💶 Budget p.p.", f"€ {per_person}")
    st.markdown("</div>", unsafe_allow_html=True)

with colD:
    st.markdown('<div class="tb-kpi">', unsafe_allow_html=True)
    st.metric("🧾 Items (draft)", len(st.session_state.draft_items))
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# Progress bar "trip completeness"
score = 0
score += 1 if trip["destination"] else 0
score += 1 if trip["budget_eur"] > 0 else 0
score += 1 if days > 0 else 0
score += 1 if len(st.session_state.draft_items) > 0 else 0
progress = score / 4

st.subheader("🚀 Trip readiness")
st.progress(progress)
labels = {
    0.0: "Nog leeg. Begin met bestemming + data.",
    0.25: "Nice, basis staat. Voeg budget of draft toe.",
    0.50: "Halfway. Tijd om je itinerary te bouwen.",
    0.75: "Bijna klaar. Check stats + finetune.",
    1.0: "Go time. Pak je koffer. 🧳",
}
closest = max([k for k in labels.keys() if k <= progress])
st.caption(labels[closest])

st.write("")