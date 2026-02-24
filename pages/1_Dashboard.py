import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# -----------------------------
# Helpers
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
        st.session_state.draft_items = []
    if "ui" not in st.session_state:
        st.session_state.ui = {"show_tips": True, "last_saved": None}
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
st.title("📊 Dashboard")
st.caption("Overzicht van je trip, budget, en planning. Alles komt uit `st.session_state`.")

# -----------------------------
# Derived values
# -----------------------------
days = (trip["end_date"] - trip["start_date"]).days + 1
days = max(days, 0)

budget = int(trip["budget_eur"])
travelers = int(trip["travelers"]) if int(trip["travelers"]) > 0 else 1
budget_pp = int(budget / travelers) if travelers else 0

items = st.session_state.draft_items
items_df = pd.DataFrame(items) if len(items) else pd.DataFrame(columns=["day", "time", "title", "cost"])

total_planned_cost = int(items_df["cost"].sum()) if len(items_df) else 0
remaining = budget - total_planned_cost

# -----------------------------
# KPI Row
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("📍 Bestemming", trip["destination"] or "—")
c2.metric("🗓️ Duur", f"{days} dagen")
c3.metric("💶 Budget p.p.", f"€ {budget_pp}")
c4.metric("🧾 Items", f"{len(items)}")

st.divider()

# -----------------------------
# Main layout
# -----------------------------
left, right = st.columns([1.25, 1])

with left:
    st.subheader("🧭 Trip status")

    # Readiness score
    score = 0
    score += 1 if trip["destination"] else 0
    score += 1 if budget > 0 else 0
    score += 1 if days > 0 else 0
    score += 1 if len(items) > 0 else 0
    progress = score / 4

    st.progress(progress)
    if progress < 0.5:
        st.warning("Nog wat basics invullen (bestemming, data, budget) en je bent vertrokken.")
    elif progress < 1.0:
        st.info("Nice! Voeg nog wat itinerary-items toe om je trip ‘af’ te maken.")
    else:
        st.success("Trip readiness: 100%. 🧳")

    st.write("")

    st.subheader("🗺️ Mini map (demo)")
    st.caption("We gebruiken een simpele demo-locatie. Later kan je echte coördinaten gebruiken.")
    demo_map = pd.DataFrame(
        [{"lat": 50.8503, "lon": 4.3517, "label": "Brussel (demo pin)"}]
    )
    st.map(demo_map, latitude="lat", longitude="lon", size=None)

    st.write("")

    st.subheader("📝 Itinerary preview")
    if len(items_df):
        items_df_sorted = items_df.sort_values(["day", "time"], ascending=[True, True])
        st.dataframe(items_df_sorted, use_container_width=True, hide_index=True)

        # Quick filters
        day_filter = st.selectbox("Filter op dag", options=["Alle"] + sorted(items_df["day"].unique().tolist()))
        if day_filter != "Alle":
            st.dataframe(items_df_sorted[items_df_sorted["day"] == day_filter], use_container_width=True, hide_index=True)

        if st.button("🧨 Clear draft items", type="secondary"):
            st.session_state.draft_items = []
            log("Draft items gewist.")
            st.rerun()
    else:
        st.info("Nog geen items. Ga naar **TripPlanner** om activiteiten toe te voegen.")

with right:
    st.subheader("💸 Budget breakdown")

    # Make a fake category split based on titles (demo logic)
    if len(items_df):
        def categorize(title: str) -> str:
            t = str(title).lower()
            if any(k in t for k in ["hotel", "hostel", "airbnb"]):
                return "Stay"
            if any(k in t for k in ["train", "metro", "flight", "bus", "taxi"]):
                return "Transport"
            if any(k in t for k in ["museum", "ticket", "tour"]):
                return "Activities"
            if any(k in t for k in ["lunch", "dinner", "ramen", "food", "pizza"]):
                return "Food"
            return "Other"

        tmp = items_df.copy()
        tmp["category"] = tmp["title"].apply(categorize)
        cat = tmp.groupby("category", as_index=False)["cost"].sum()

        fig = px.pie(cat, names="category", values="cost", title="Geplande kosten per categorie")
        st.plotly_chart(fig, use_container_width=True)

        st.metric("✅ Gepland", f"€ {total_planned_cost}")
        st.metric("🧾 Remaining", f"€ {remaining}")

        if remaining < 0:
            st.error("Je zit over budget. Tijd om te schrappen of budget te verhogen.")
        elif remaining < 100:
            st.warning("Je zit dicht bij je budget.")
        else:
            st.success("Je hebt nog ruimte in je budget.")
    else:
        st.info("Geen itinerary costs gevonden. Voeg items toe met kosten om charts te zien.")
        st.metric("🧾 Budget", f"€ {budget}")

    st.write("")

    st.subheader("📦 Export (demo)")
    st.caption("We exporteren naar CSV/JSON vanuit session_state.")

    export_col1, export_col2 = st.columns(2)

    with export_col1:
        if len(items_df):
            csv_bytes = items_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download itinerary.csv",
                data=csv_bytes,
                file_name="itinerary.csv",
                mime="text/csv",
            )
        else:
            st.button("⬇️ Download itinerary.csv", disabled=True)

    with export_col2:
        # Trip JSON export
        import json
        trip_json = json.dumps(
            {"trip": trip, "draft_items": st.session_state.draft_items},
            indent=2,
            default=str,
        ).encode("utf-8")
        st.download_button(
            "⬇️ Download trip.json",
            data=trip_json,
            file_name="trip.json",
            mime="application/json",
        )

    st.write("")

    st.subheader("🧾 Activity log")
    if st.session_state.activity:
        for line in st.session_state.activity[:10]:
            st.write("•", line)
    else:
        st.caption("Nog geen acties gelogd.")