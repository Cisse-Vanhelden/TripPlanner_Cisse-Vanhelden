import streamlit as st
from datetime import date, timedelta

st.set_page_config(page_title="Trip Planner", page_icon="🗺️", layout="wide")

# -----------------------------
# State init
# -----------------------------
def ensure_state():
    if "trip" not in st.session_state:
        st.session_state.trip = {
            "destination": "",
            "start_date": date.today(),
            "end_date": date.today(),
            "budget_eur": 0,
            "travelers": 1,
            "interests": [],
            "notes": "",
        }
    if "draft_items" not in st.session_state:
        st.session_state.draft_items = []  # list[dict]
    if "activity" not in st.session_state:
        st.session_state.activity = []  # list[str]

def log(msg: str):
    st.session_state.activity.insert(0, msg)
    st.session_state.activity = st.session_state.activity[:30]

ensure_state()
trip = st.session_state.trip

# -----------------------------
# Header
# -----------------------------
st.title("🗺️ Trip Planner")
st.caption("Stel je trip in en voeg activiteiten toe aan je itinerary (via session_state).")

# -----------------------------
# Trip settings (left) + Quick stats (right)
# -----------------------------
left, right = st.columns([1.15, 0.85])

with left:
    st.subheader("⚙️ Trip instellingen")

    c1, c2 = st.columns(2)
    with c1:
        destination = st.text_input("Bestemming", value=trip["destination"])
    with c2:
        travelers = st.number_input("Reizigers", min_value=1, max_value=20, value=int(trip["travelers"]), step=1)

    c3, c4 = st.columns(2)
    with c3:
        start_date = st.date_input("Startdatum", value=trip["start_date"])
    with c4:
        end_date = st.date_input("Einddatum", value=trip["end_date"])

    budget = st.slider("Budget (€)", 0, 10000, int(trip["budget_eur"]), step=50)

    interests = st.multiselect(
        "Interesses",
        ["Food", "Culture", "Nature", "Nightlife", "Museums", "Shopping", "Tech", "Beaches", "History"],
        default=trip.get("interests", []),
    )

    notes = st.text_area("Notes (optioneel)", value=trip.get("notes", ""), height=120)

    save_col1, save_col2 = st.columns(2)
    with save_col1:
        if st.button("💾 Save trip settings", type="primary"):
            trip["destination"] = destination
            trip["travelers"] = int(travelers)
            trip["start_date"] = start_date
            trip["end_date"] = end_date
            trip["budget_eur"] = int(budget)
            trip["interests"] = interests
            trip["notes"] = notes
            log(f"Trip settings saved: {trip['destination']} • €{trip['budget_eur']} • {trip['travelers']} traveler(s)")
            st.success("Opgeslagen!")
    with save_col2:
        if st.button("➡️ Ga naar Itinerary"):
            st.switch_page("pages/Itinerary.py")

with right:
    st.subheader("📌 Quick stats")
    days = (trip["end_date"] - trip["start_date"]).days + 1
    days = max(days, 0)

    budget_pp = int(trip["budget_eur"] / max(1, int(trip["travelers"])))

    st.metric("Bestemming", trip["destination"] or "—")
    st.metric("Duur", f"{days} dagen")
    st.metric("Budget", f"€ {trip['budget_eur']}")
    st.metric("Budget p.p.", f"€ {budget_pp}")
    st.write("")
    st.info("Tip: eerst trip opslaan, dan activities toevoegen.")

st.divider()

# -----------------------------
# Activity templates (starter catalog)
# -----------------------------
st.subheader("🎯 Activity Builder")

templates = [
    {"title": "City walking tour", "category": "Activities", "cost": 25, "time": "10:00"},
    {"title": "Museum visit", "category": "Museums", "cost": 18, "time": "11:00"},
    {"title": "Lunch at local spot", "category": "Food", "cost": 20, "time": "13:00"},
    {"title": "Public transport day pass", "category": "Transport", "cost": 9, "time": "09:00"},
    {"title": "Sunset viewpoint", "category": "Nature", "cost": 0, "time": "19:00"},
    {"title": "Dinner reservation", "category": "Food", "cost": 35, "time": "20:00"},
]

if "template_pick" not in st.session_state:
    st.session_state.template_pick = templates[0]["title"]

tcol1, tcol2, tcol3 = st.columns([1.2, 0.9, 0.9])

with tcol1:
    template_choice = st.selectbox(
        "Kies een template (optioneel)",
        [t["title"] for t in templates],
        index=0,
        key="template_pick",
    )

picked = next(t for t in templates if t["title"] == template_choice)

with tcol2:
    st.write("**Category**")
    st.write(picked["category"])
with tcol3:
    st.write("**Default cost**")
    st.write(f"€ {picked['cost']}")

st.write("")

# -----------------------------
# Add activity form (no rerun until submit)
# -----------------------------
days = (trip["end_date"] - trip["start_date"]).days + 1
days = max(days, 1)  # minimum 1 voor day selector

with st.form("add_activity_form", clear_on_submit=True):
    f1, f2, f3 = st.columns([1, 1, 1])

    with f1:
        day = st.selectbox("Dag", list(range(1, days + 1)))
        time_str = st.text_input("Tijd (HH:MM)", value=picked["time"])
    with f2:
        title = st.text_input("Activiteit", value=picked["title"])
        category = st.selectbox(
            "Categorie",
            ["Activities", "Museums", "Food", "Transport", "Nature", "Shopping", "Nightlife", "Other"],
            index=["Activities", "Museums", "Food", "Transport", "Nature", "Shopping", "Nightlife", "Other"].index(
                picked["category"] if picked["category"] in ["Activities", "Museums", "Food", "Transport", "Nature", "Shopping", "Nightlife", "Other"] else "Other"
            ),
        )
    with f3:
        cost = st.number_input("Kost (€)", min_value=0, max_value=5000, value=int(picked["cost"]), step=1)
        tags = st.text_input("Tags (comma-separated)", value="")

    submitted = st.form_submit_button("➕ Add to itinerary")

if submitted:
    item = {
        "day": int(day),
        "time": time_str.strip(),
        "title": title.strip(),
        "category": category,
        "cost": int(cost),
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
    }
    st.session_state.draft_items.append(item)
    log(f"Added: Day {item['day']} • {item['time']} • {item['title']} (€{item['cost']})")
    st.toast("Activity toegevoegd!", icon="✅")
    st.rerun()

# -----------------------------
# Preview + quick edits
# -----------------------------
st.write("")
st.subheader("🧾 Current draft (preview)")

if not st.session_state.draft_items:
    st.info("Nog niets toegevoegd. Gebruik het formulier hierboven.")
else:
    # Sort preview
    items_sorted = sorted(st.session_state.draft_items, key=lambda x: (x.get("day", 0), x.get("time", "")))

    # Show as dataframe
    import pandas as pd
    df = pd.DataFrame(items_sorted)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Quick tools
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("🔀 Sort by day/time"):
            st.session_state.draft_items = items_sorted
            log("Draft sorted by day/time.")
            st.rerun()

    with q2:
        if st.button("🧽 Remove last item"):
            removed = st.session_state.draft_items.pop() if st.session_state.draft_items else None
            if removed:
                log(f"Removed last: {removed['title']}")
                st.rerun()

    with q3:
        if st.button("🧨 Clear all"):
            st.session_state.draft_items = []
            log("Cleared all draft items.")
            st.rerun()

st.divider()

# -----------------------------
# Next steps
# -----------------------------
st.subheader("➡️ Next steps")
n1, n2 = st.columns(2)
with n1:
    st.write("Ga naar **Itinerary** om per dag te bekijken en items te verwijderen.")
    if st.button("📅 Open Itinerary"):
        st.switch_page("pages/3_Itinerary.py")
with n2:
    st.write("Ga naar **Dashboard** om charts en export te zien.")
    if st.button("📊 Open Dashboard"):
        st.switch_page("pages/1_Dashboard.py")