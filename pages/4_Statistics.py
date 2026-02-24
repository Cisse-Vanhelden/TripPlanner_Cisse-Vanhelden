import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Statistics", page_icon="📊", layout="wide")

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
        st.session_state.draft_items = []
    if "activity" not in st.session_state:
        st.session_state.activity = []

ensure_state()
trip = st.session_state.trip
items = st.session_state.draft_items

st.title("📊 Statistics")
st.caption("Analyse van je trip: budget health, kostenverdeling en planning trends.")

# -----------------------------
# Prepare dataframe
# -----------------------------
if items:
    df = pd.DataFrame(items).copy()
else:
    df = pd.DataFrame(columns=["day", "time", "title", "category", "cost", "tags"])

# Normalize types
if "cost" in df.columns:
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce").fillna(0).astype(int)
if "day" in df.columns:
    df["day"] = pd.to_numeric(df["day"], errors="coerce").fillna(0).astype(int)

budget = int(trip.get("budget_eur", 0))
travelers = int(trip.get("travelers", 1)) if int(trip.get("travelers", 1)) > 0 else 1
days = (trip["end_date"] - trip["start_date"]).days + 1
days = max(days, 0)

planned = int(df["cost"].sum()) if len(df) else 0
remaining = budget - planned

# -----------------------------
# KPI Row
# -----------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("📍 Bestemming", trip.get("destination") or "—")
k2.metric("💶 Budget", f"€ {budget}")
k3.metric("✅ Planned", f"€ {planned}")
k4.metric("🧾 Remaining", f"€ {remaining}")

# Budget health message
if budget <= 0:
    st.warning("Je budget staat op €0. Zet een budget in TripPlanner.")
elif remaining < 0:
    st.error("Je zit over budget. Tijd om te schrappen of budget te verhogen.")
elif remaining < 100:
    st.warning("Je zit dicht bij je budget.")
else:
    st.success("Budget ziet er gezond uit.")

st.divider()

# -----------------------------
# Layout
# -----------------------------
left, right = st.columns([1.1, 0.9])

with left:
    st.subheader("📅 Spending per day")

    if len(df):
        by_day = df.groupby("day", as_index=False)["cost"].sum().sort_values("day")
        by_day["Day"] = by_day["day"].apply(lambda x: f"Dag {x}")

        fig_day = px.bar(by_day, x="Day", y="cost", title="Kosten per dag")
        st.plotly_chart(fig_day, use_container_width=True)

        # Optional line trend
        fig_line = px.line(by_day, x="Day", y="cost", markers=True, title="Trend (kosten per dag)")
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Geen items om per dag te analyseren. Voeg activities toe in TripPlanner.")

with right:
    st.subheader("🍱 Spending per category")

    if len(df):
        if "category" not in df.columns:
            df["category"] = "Other"

        by_cat = df.groupby("category", as_index=False)["cost"].sum().sort_values("cost", ascending=False)

        fig_cat = px.pie(by_cat, names="category", values="cost", hole=0.45, title="Verdeling per categorie")
        st.plotly_chart(fig_cat, use_container_width=True)

        # Show top categories table
        st.dataframe(by_cat, use_container_width=True, hide_index=True)
    else:
        st.info("Geen items om categorieën te analyseren.")

st.divider()

# -----------------------------
# Top expensive items
# -----------------------------
st.subheader("💎 Top expensive items")

if len(df):
    top_n = st.slider("Hoeveel tonen?", 3, 15, 5)
    top = df.sort_values("cost", ascending=False).head(top_n)

    fig_top = px.bar(
        top,
        x="cost",
        y="title",
        orientation="h",
        title="Duurste activiteiten",
    )
    st.plotly_chart(fig_top, use_container_width=True)

    st.dataframe(top[["day", "time", "title", "category", "cost"]].sort_values(["day", "time"]), use_container_width=True, hide_index=True)
else:
    st.info("Nog geen items. Voeg eerst itinerary items toe.")

st.divider()

# -----------------------------
# Budget per person + per day
# -----------------------------
st.subheader("🧮 Budget breakdown (per person / per day)")

b1, b2, b3, b4 = st.columns(4)

budget_pp = int(budget / travelers) if travelers else 0
planned_pp = int(planned / travelers) if travelers else 0

budget_per_day = int(budget / days) if days > 0 else 0
planned_per_day = int(planned / days) if days > 0 else 0

b1.metric("Budget p.p.", f"€ {budget_pp}")
b2.metric("Planned p.p.", f"€ {planned_pp}")
b3.metric("Budget / dag", f"€ {budget_per_day}")
b4.metric("Planned / dag", f"€ {planned_per_day}")

# -----------------------------
# Navigation
# -----------------------------
nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("🏁 Dashboard"):
        st.switch_page("pages/Dashboard.py")
with nav2:
    if st.button("🗺️ TripPlanner"):
        st.switch_page("pages/TripPlanner.py")
with nav3:
    if st.button("📅 Itinerary"):
        st.switch_page("pages/Itinerary.py")