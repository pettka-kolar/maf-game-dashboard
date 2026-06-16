import streamlit as st
import pandas as pd
import json
import os
import importlib  # 💡 Added: Enables manual cache busting for imported files

# Cross-reference database definitions to identify console vs steam tracks natively
import game_database as gd
importlib.reload(gd)  # 💡 Added: Forces Streamlit to always pull the newest game_database.py from disk

METRICS_FILE = "metrics.json"

st.set_page_config(page_title="Gaming Metrics Dashboard", page_icon="🎮", layout="wide")

st.title("🎮 Real-Time Video Game Metrics Dashboard")
st.markdown("This serverless dashboard displays metrics automatically kept current by background GitHub Action triggers.")

# Read metrics snapshot data safely
if not os.path.exists(METRICS_FILE):
    st.warning("Data file initializing. Run worker.py locally or activate your GitHub Workflow task.")
else:
    with open(METRICS_FILE, "r") as f:
        raw_data = json.load(f)
    
    rows = []
    for game_name, metrics in raw_data.items():
        # Look up the steam ID from our configuration module dynamically
        steam_id = gd.GAME_DATABASE.get(game_name, {}).get("steam_id", 0)
        
        rows.append({
            "Game Title": game_name,
            "steam_id": steam_id,  # Retained temporarily for dataframe filtering splits
            "Release Date": metrics.get("release_date"),
            "Live CCU (Steam)": metrics.get("live_ccu"),
            "All-Time Peak": metrics.get("all_time_peak"),
            "Steam Rating %": metrics.get("steam_rating"),
            "Total Steam Reviews": metrics.get("total_reviews"),
            "OpenCritic Score": metrics.get("opencritic_score"),
            "Metacritic Score": metrics.get("metacritic_score"),
            # Automatically build the link parameter if it's a valid Steam entity
            "SteamDB": f"https://steamdb.info/app/{steam_id}/" if steam_id != 0 else None
        })
    df = pd.DataFrame(rows)

if not df.empty:
    # CRITICAL FIX: Add format="mixed" to correctly parse heterogeneous date formats seamlessly
    df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce", format="mixed")
    df["Release Date"] = df["Release Date"].fillna(pd.to_datetime("2099-01-01"))

    # Dynamic lookback window matching requirements
    current_time = pd.Timestamp.now().normalize()
    fifteen_days_ago = current_time - pd.Timedelta(days=15)
    df = df[df["Release Date"] >= fifteen_days_ago]

    # Convert all numeric data columns cleanly
    numeric_columns = ["Live CCU (Steam)", "All-Time Peak", "Steam Rating %", "Total Steam Reviews", "OpenCritic Score", "Metacritic Score"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # -------------------------------------------------------------------------
    # TABLE DIVISION 1: PC / STEAM TRACKS
    # -------------------------------------------------------------------------
    st.subheader("🖥️ PC & Steam Tracking Node")
    
    df_steam = df[df["steam_id"] != 0].copy()
    if not df_steam.empty:
        # Sort PC tracks by their Steam review scores
        df_steam = df_steam.sort_values(by="Steam Rating %", ascending=False, na_position="last")
        df_steam = df_steam.drop(columns=["steam_id"])
        
        dynamic_height_steam = (len(df_steam) + 1) * 35 + 10
        
        st.dataframe(
            df_steam,
            column_config={
                "Game Title": st.column_config.TextColumn(width="medium"),
                "Release Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
                "Live CCU (Steam)": st.column_config.NumberColumn(format="%d"),
                "All-Time Peak": st.column_config.NumberColumn(format="%d"),
                "Steam Rating %": st.column_config.NumberColumn(format="%.2f%%"),
                "Total Steam Reviews": st.column_config.NumberColumn(format="%d"),
                "OpenCritic Score": st.column_config.NumberColumn(format="%d"),
                "Metacritic Score": st.column_config.NumberColumn(format="%d"),
                # Render SteamDB URLs as an elegant clickable anchor link icon
                "SteamDB": st.column_config.LinkColumn(display_text="🔗 Link"),
            },
            hide_index=True,
            width="stretch",
            height=dynamic_height_steam
        )
    else:
        st.info("No Steam releases currently within the tracking window viewport.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # TABLE DIVISION 2: CONSOLE EXCLUSIVE TRACKS
    # -------------------------------------------------------------------------
    st.subheader("🎮 Console Exclusive / First Tracks")
    
    df_console = df[df["steam_id"] == 0].copy()
    if not df_console.empty:
        # Sort console tracks by OpenCritic values since Steam metrics don't apply
        df_console = df_console.sort_values(by="OpenCritic Score", ascending=False, na_position="last")
        
        # Isolate the viewport to show only console-relevant parameters
        df_console = df_console[["Game Title", "Release Date", "OpenCritic Score", "Metacritic Score"]]
        
        dynamic_height_console = (len(df_console) + 1) * 35 + 10
        
        st.dataframe(
            df_console,
            column_config={
                "Game Title": st.column_config.TextColumn(width="medium"),
                "Release Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
                "OpenCritic Score": st.column_config.NumberColumn(format="%d"),
                "Metacritic Score": st.column_config.NumberColumn(format="%d"),
            },
            hide_index=True,
            width="stretch",
            height=dynamic_height_console
        )
    else:
        st.info("No Console-first exclusives currently within the tracking window viewport.")

    st.caption("Ecosystem Status: Active. Public presentation data synchronized.")