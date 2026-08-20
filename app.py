import streamlit as st
import pandas as pd
import json
import os
import importlib

# Cross-reference database definitions to identify console vs steam tracks natively
import game_database as gd
importlib.reload(gd)

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
        # Look up the game configuration profile dynamically
        game_config = gd.GAME_DATABASE.get(game_name, {})
        steam_id = game_config.get("steam_id", 0)
        origin = game_config.get("origin")
        
        # Prioritize manual date from game_database.py. If missing, fall back to metrics.json
        release_date = game_config.get("release_date") or metrics.get("release_date")
        
        rows.append({
            "Game Title": game_name,
            "Origin": origin if origin else "—",
            "Tags": metrics.get("tags", "—"),
            "steam_id": steam_id,
            "Release Date": release_date,
            "Live CCU (Steam)": metrics.get("live_ccu"),
            "All-Time Peak": metrics.get("all_time_peak"),
            "Steam Rating %": metrics.get("steam_rating"),
            "Total Steam Reviews": metrics.get("total_reviews"),
            "OpenCritic Score": metrics.get("opencritic_score"),
            "Metacritic Score": metrics.get("metacritic_score"),
            "SteamDB": f"https://steamdb.info/app/{steam_id}/" if steam_id != 0 else None
        })
    df = pd.DataFrame(rows)

if not df.empty:
    # Add format="mixed" to correctly parse heterogeneous date formats seamlessly
    df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce", format="mixed")
    df["Release Date"] = df["Release Date"].fillna(pd.to_datetime("2099-01-01"))

    # Dynamic lookback window matching requirements
    current_time = pd.Timestamp.now().normalize()
    fifteen_days_ago = current_time - pd.Timedelta(days=15)
    df = df[df["Release Date"] >= fifteen_days_ago]

    # Convert datetime objects to standard ISO strings for clean output formatting
    df["Release Date"] = df["Release Date"].dt.strftime('%Y-%m-%d').replace("2099-01-01", "To be released")

    # Convert all numeric data columns cleanly
    numeric_columns = ["Live CCU (Steam)", "All-Time Peak", "Steam Rating %", "Total Steam Reviews", "OpenCritic Score", "Metacritic Score"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Set up combined row styling (bolding for released titles + soft blue tint for local CZ/SK titles)
    current_time_str = current_time.strftime('%Y-%m-%d')
    
    def style_rows(row):
        rel_date = row.get("Release Date", "")
        origin = row.get("Origin", "")
        
        is_released = (rel_date != "To be released" and rel_date <= current_time_str)
        is_local = origin in ("CZ", "SK")
        
        style_rules = []
        if is_released:
            style_rules.append("font-weight: bold;")
        if is_local:
            style_rules.append("background-color: rgba(66, 133, 244, 0.12);")
            
        style_str = " ".join(style_rules)
        return [style_str] * len(row)

    # -------------------------------------------------------------------------
    # TABLE DIVISION 1: PC / STEAM TRACKS
    # -------------------------------------------------------------------------
    st.subheader("🖥️ PC & Steam Tracking Node")
    
    df_steam = df[df["steam_id"] != 0].copy()
    if not df_steam.empty:
        # Sort PC tracks by their Steam review scores
        df_steam = df_steam.sort_values(by="Steam Rating %", ascending=False, na_position="last")
        df_steam = df_steam.drop(columns=["steam_id"])
        
        # Explicit column ordering with Origin placed beside Game Title
        column_order = [
            "Game Title", "Origin", "Tags", "Release Date", "Live CCU (Steam)", 
            "All-Time Peak", "Steam Rating %", "Total Steam Reviews", 
            "OpenCritic Score", "Metacritic Score", "SteamDB"
        ]
        df_steam = df_steam[column_order]
        
        # Apply combined styling to the final display frame
        styled_steam = df_steam.style.apply(style_rows, axis=1)
        
        dynamic_height_steam = (len(df_steam) + 1) * 35 + 10
        
        st.dataframe(
            styled_steam,
            column_config={
                "Game Title": st.column_config.TextColumn(width="medium"),
                "Origin": st.column_config.TextColumn(width="small", help="Country of origin (CZ / SK)"),
                "Tags": st.column_config.TextColumn(width="medium", help="Top popular user tags from Steam"),
                "Release Date": st.column_config.TextColumn(width="small"),
                "Live CCU (Steam)": st.column_config.NumberColumn(format="%d"),
                "All-Time Peak": st.column_config.NumberColumn(format="%d"),
                "Steam Rating %": st.column_config.NumberColumn(format="%.2f%%"),
                "Total Steam Reviews": st.column_config.NumberColumn(format="%d"),
                "OpenCritic Score": st.column_config.NumberColumn(format="%d"),
                "Metacritic Score": st.column_config.NumberColumn(format="%d"),
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
        df_console = df_console.sort_values(by="OpenCritic Score", ascending=False, na_position="last")
        # Isolate the viewport to show console-relevant parameters and origin
        df_console = df_console[["Game Title", "Origin", "Release Date", "OpenCritic Score", "Metacritic Score"]]
        
        # Apply combined styling to the final display frame
        styled_console = df_console.style.apply(style_rows, axis=1)
        
        dynamic_height_console = (len(df_console) + 1) * 35 + 10
        
        st.dataframe(
            styled_console,
            column_config={
                "Game Title": st.column_config.TextColumn(width="medium"),
                "Origin": st.column_config.TextColumn(width="small", help="Country of origin (CZ / SK)"),
                "Release Date": st.column_config.TextColumn(width="small"),
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