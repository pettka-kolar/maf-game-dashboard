import streamlit as st
import pandas as pd
import json
import os

METRICS_FILE = "metrics.json"

st.set_page_config(page_title="Gaming Metrics Dashboard", page_icon="🎮", layout="wide")

st.title("🎮 Real-Time Video Game Metrics Dashboard")
st.markdown("This serverless dashboard displays metrics automatically kept current by background GitHub Action triggers.")

# Read metrics snapshot data safely
if not os.path.exists(METRICS_FILE):
    st.warning("Data file initializing. Run worker.py locally or activate your GitHub Workflow task.")
    df = pd.DataFrame()
else:
    with open(METRICS_FILE, "r") as f:
        raw_data = json.load(f)
    
    rows = []
    for game_name, metrics in raw_data.items():
        rows.append({
            "Game Title": game_name,
            "Release Date": metrics.get("release_date"),
            "Live CCU (Steam)": metrics.get("live_ccu"),
            "All-Time Peak": metrics.get("all_time_peak"),
            "Steam Rating %": metrics.get("steam_rating"),
            "Total Steam Reviews": metrics.get("total_reviews"),
            "OpenCritic Score": metrics.get("opencritic_score"),
            "Metacritic Score": metrics.get("metacritic_score")
        })
    df = pd.DataFrame(rows)

if not df.empty:
    df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce")
    df["Release Date"] = df["Release Date"].fillna(pd.to_datetime("2099-01-01"))

    # Dynamic lookback window matching requirements
    current_time = pd.Timestamp.now().normalize()
    fifteen_days_ago = current_time - pd.Timedelta(days=15)
    df = df[df["Release Date"] >= fifteen_days_ago]

    numeric_columns = ["Live CCU (Steam)", "All-Time Peak", "Steam Rating %", "Total Steam Reviews", "OpenCritic Score", "Metacritic Score"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(by="Steam Rating %", ascending=False, na_position="last")
    dynamic_height = (len(df) + 1) * 35 + 10

    st.dataframe(
        df,
        column_config={
            "Game Title": st.column_config.TextColumn(width="medium"),
            "Release Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Live CCU (Steam)": st.column_config.NumberColumn(format="%d"),
            "All-Time Peak": st.column_config.NumberColumn(format="%d"),
            "Steam Rating %": st.column_config.NumberColumn(format="%.2f%%"),
            "Total Steam Reviews": st.column_config.NumberColumn(format="%d"),
            "OpenCritic Score": st.column_config.NumberColumn(format="%d"),
            "Metacritic Score": st.column_config.NumberColumn(format="%d"),
        },
        hide_index=True,
        width="stretch",
        height=dynamic_height
    )
    st.caption("Ecosystem Status: Active. Public presentation data synchronized.")