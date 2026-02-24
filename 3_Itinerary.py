import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Itinerary", page_icon="📅", layout="wide")

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

def log(msg: str):
    st.session_state.activity.insert(0, msg)
    st.session_state.activity = st.session_state.activity[:30]

ensure_state()
trip = st.session_state.trip

st.title("📅 Itinerary")
st.caption("Beheer je dagplanning: bekijken, sorteren, verplaatsen en verwijderen.")

# -----------------------------
# Derived values
# -----------------------------
days = (trip["end_date"] - trip["start_date"]).days + 1
days = max(days, 1)

items = st.session_state.draft_items

# -----------------------------
# Controls
# -----------------------------
top1, top2, top3, top4 = st.columns([1.2, 1.2, 1.2, 1.4])

with top1:
    day_filter = st.selectbox("Filter op dag", options=["Alle"] + [f"Dag {i}" for i in range(1, days + 1)], index=0)

with top2:
    sort_mode = st.selectbox("Sorteren", options=["Day + Time", "Cost (high→low)", "Title (A→Z)"], index=0)

with top3:
    compact = st.toggle("Compact view", value=False)

with top4:
    if st.button("🧭 Terug naar TripPlanner"):
        st.switch_page("pages/TripPlanner.py")

# -----------------------------
# Helper functions for ordering & operations
# -----------------------------
def normalize_time(t: str) -> str:
    # Very simple normalization, keeps HH:MM if possible
    t = (t or "").strip()
    if len(t) == 4 and t[1] == ":":
        t = "0" + t
    return t

def apply_sort(data: list[dict]) -> list[dict]:
    if sort_mode == "Day + Time":
        return sorted(data, key=lambda x: (int(x.get("day", 0)), normalize_time(x.get("time", "")), x.get("title", "")))
    if sort_mode == "Cost (high→low)":
        return sorted(data, key=lambda x: int(x.get("cost", 0)), reverse=True)
    return sorted(data, key=lambda x: str(x.get("title", "")).lower())

def remove_item(index: int):
    item = st.session_state.draft_items.pop(index)
    log(f"Removed: Day {item.get('day')} • {item.get('title')}")
    st.rerun()

def move_item(index: int, direction: int):
    # direction: -1 for up, +1 for down
    new_index = index + direction
    if new_index < 0 or new_index >= len(st.session_state.draft_items):
        return
    st.session_state.draft_items[index], st.session_state.draft_items[new_index] = (
        st.session_state.draft_items[new_index],
        st.session_state.draft_items[index],
    )
    log(f"Moved item {'up' if direction == -1 else 'down'} at position {index}")
    st.rerun()

# -----------------------------
# Empty state
# -----------------------------
if not items:
    st.info("Nog geen itinerary items. Ga naar TripPlanner en voeg activiteiten toe.")
    if st.button("➕ Open TripPlanner"):
        st.switch_page("pages/TripPlanner.py")
    st.stop()

# -----------------------------
# Prepare view data
# -----------------------------
view_items = apply_sort(items)

# Filter by day
if day_filter != "Alle":
    day_num = int(day_filter.replace("Dag ", ""))
    view_items = [x for x in view_items if int(x.get("day", 0)) == day_num]

# We'll also compute totals per day from original list (not filtered)
df_all = pd.DataFrame(items)
df_all["cost"] = pd.to_numeric(df_all.get("cost", 0), errors="coerce").fillna(0).astype(int)
totals_per_day = df_all.groupby("day", as_index=False)["cost"].sum().sort_values("day")

# -----------------------------
# Summary row
# -----------------------------
sum1, sum2, sum3, sum4 = st.columns(4)
sum1.metric("📍 Bestemming", trip["destination"] or "—")
sum2.metric("🧾 Items (totaal)", len(items))
sum3.metric("💰 Totale kost", f"€ {int(df_all['cost'].sum())}")
sum4.metric("🗓️ Dagen", f"{days}")

st.divider()

# -----------------------------
# Day-by-day planner view
# -----------------------------
if day_filter == "Alle":
    day_range = range(1, days + 1)
else:
    day_range = [int(day_filter.replace("Dag ", ""))]

for d in day_range:
    st.subheader(f"Dag {d}")

    # Day total
    day_total = int(totals_per_day.loc[totals_per_day["day"] == d, "cost"].sum()) if len(totals_per_day) else 0
    st.caption(f"Totale geplande kost voor dag {d}: € {day_total}")

    # Items for this day (respecting current sort/filter)
    day_items = [x for x in view_items if int(x.get("day", 0)) == d]

    if not day_items:
        st.info("Geen items voor deze dag.")
        continue

    # Show each item as a card-like row with actions
    for idx_in_view, item in enumerate(day_items):
        # We need the actual index in the original list to delete/move reliably
        # Find first matching dict by identity/fields (safe enough for this project)
        orig_index = None
        for j, orig in enumerate(st.session_state.draft_items):
            if orig is item:
                orig_index = j
                break
        if orig_index is None:
            # fallback (match fields)
            for j, orig in enumerate(st.session_state.draft_items):
                if orig.get("day") == item.get("day") and orig.get("time") == item.get("time") and orig.get("title") == item.get("title"):
                    orig_index = j
                    break

        time_str = item.get("time", "")
        title = item.get("title", "")
        category = item.get("category", "Other")
        cost = int(item.get("cost", 0))
        tags = item.get("tags", [])

        c1, c2, c3, c4, c5 = st.columns([0.9, 3.4, 1.3, 1.1, 1.3])

        with c1:
            st.write(f"**{time_str}**" if time_str else "—")

        with c2:
            st.write(f"**{title}**")
            meta = f"{category}"
            if tags:
                meta += " • " + ", ".join(tags)
            st.caption(meta)

        with c3:
            st.write(f"€ {cost}")

        with c4:
            # Move up/down within full list (not per-day), simple but works well
            up = st.button("⬆️", key=f"up_{d}_{idx_in_view}")
            down = st.button("⬇️", key=f"down_{d}_{idx_in_view}")
            if orig_index is not None:
                if up:
                    move_item(orig_index, -1)
                if down:
                    move_item(orig_index, +1)

        with c5:
            if st.button("🗑️ Delete", key=f"del_{d}_{idx_in_view}"):
                if orig_index is not None:
                    remove_item(orig_index)

    if not compact:
        st.write("")  # spacer

st.divider()

# -----------------------------
# Table view + quick export preview
# -----------------------------
st.subheader("📋 Table view (alle items)")
df_view = pd.DataFrame(apply_sort(items))
df_view["cost"] = pd.to_numeric(df_view.get("cost", 0), errors="coerce").fillna(0).astype(int)
st.dataframe(df_view.sort_values(["day", "time"]), use_container_width=True, hide_index=True)

b1, b2, b3 = st.columns(3)
with b1:
    if st.button("🧹 Clear all items"):
        st.session_state.draft_items = []
        log("Cleared all itinerary items.")
        st.rerun()

with b2:
    if st.button("📊 Open Statistics"):
        st.switch_page("pages/Statistics.py")

with b3:
    if st.button("🏁 Open Dashboard"):
        st.switch_page("pages/Dashboard.py")