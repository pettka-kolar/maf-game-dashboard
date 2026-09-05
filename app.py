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

def format_price_pair(discounted_release, full_price):
    if discounted_release == 0 and full_price == 0:
        return "Free"
    if isinstance(discounted_release, (int, float)) and isinstance(full_price, (int, float)):
        return f"€{discounted_release:.2f} / €{full_price:.2f}"
    if isinstance(full_price, (int, float)):
        return f"€{full_price:.2f} / €{full_price:.2f}"
    if isinstance(discounted_release, (int, float)):
        return f"€{discounted_release:.2f} / €{discounted_release:.2f}"
    return "—"

# Read metrics snapshot data safely
if not os.path.exists(METRICS_FILE):
    st.warning("Data file initializing. Run worker.py locally or activate your GitHub Workflow task.")
else:
    with open(METRICS_FILE, "r") as f:
        raw_data = json.load(f)
    
    rows = []
    for game_name, metrics in raw_data.items():
        game_config = gd.GAME_DATABASE.get(game_name, {})
        steam_id = game_config.get("steam_id", 0)
        origin = game_config.get("origin")
        
        release_date = game_config.get("release_date") or metrics.get("release_date")
        
        # Cleaned pricing extraction
        price_full = metrics.get("price_full_eur")
        price_disc_rel = metrics.get("price_release_discounted_eur", price_full)
        release_discount = metrics.get("discount_release_pct", 0)
        
        rows.append({
            "Game Title": game_name,
            "Origin": origin if origin else "—",
            "Tags": metrics.get("tags", "—"),
            "steam_id": steam_id,
            "Release Date": release_date,
            "Price (EUR)": format_price_pair(price_disc_rel, price_full),
            "Release Discount %": release_discount,
            "Followers (Initial)": metrics.get("followers_initial"),
            "Followers (Release)": metrics.get("followers_release"),
            "Followers (Current)": metrics.get("followers_current"),
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
    df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce", format="mixed")
    df["Release Date"] = df["Release Date"].fillna(pd.to_datetime("2099-01-01"))

    # -------------------------------------------------------------------------
    # INTERACTIVE DATE FILTER
    # -------------------------------------------------------------------------
    current_time = pd.Timestamp.now().normalize()
    default_cutoff_date = (current_time - pd.Timedelta(days=15)).date()

    col_filter, _ = st.columns([1, 3])
    with col_filter:
        selected_cutoff = st.date_input(
            "📅 Select Release Cutoff Date:",
            value=default_cutoff_date,
            help="Filter to show games released on or after this date (or scheduled for future release)."
        )

    cutoff_timestamp = pd.to_datetime(selected_cutoff)
    df = df[df["Release Date"] >= cutoff_timestamp]

    df["Release Date"] = df["Release Date"].dt.strftime('%Y-%m-%d').replace("2099-01-01", "To be released")

    # Numeric columns to parse
    numeric_columns = [
        "Release Discount %", 
        "Followers (Initial)", "Followers (Release)", "Followers (Current)",
        "Live CCU (Steam)", "All-Time Peak", "Steam Rating %", 
        "Total Steam Reviews", "OpenCritic Score", "Metacritic Score"
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

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
        df_steam = df_steam.sort_values(by="Steam Rating %", ascending=False, na_position="last")
        df_steam = df_steam.drop(columns=["steam_id"])
        
        column_order = [
            "Game Title", "Origin", "Tags", "Release Date",
            "Live CCU (Steam)", "All-Time Peak", "Steam Rating %", 
            "Total Steam Reviews", "OpenCritic Score", "Metacritic Score", "SteamDB",
            "Price (EUR)", "Release Discount %",
            "Followers (Initial)", "Followers (Release)", "Followers (Current)"
        ]
        df_steam = df_steam[column_order]
        
        styled_steam = df_steam.style.apply(style_rows, axis=1)
        dynamic_height_steam = (len(df_steam) + 1) * 35 + 10
        
        st.dataframe(
            styled_steam,
            column_config={
                "Game Title": st.column_config.TextColumn(width="medium"),
                "Origin": st.column_config.TextColumn(width="small", help="Country of origin (CZ / SK)"),
                "Tags": st.column_config.TextColumn(width="medium", help="Top popular user tags from Steam"),
                "Release Date": st.column_config.TextColumn(width="small"),
                "Price (EUR)": st.column_config.TextColumn(width="small", help="Discounted Release Price / Full Base Price (EUR)"),
                "Release Discount %": st.column_config.NumberColumn(format="-%d%%", help="Official launch discount percentage"),
                "Followers (Initial)": st.column_config.NumberColumn(format="%d", help="Follower count when first tracked"),
                "Followers (Release)": st.column_config.NumberColumn(format="%d", help="Follower count at release date"),
                "Followers (Current)": st.column_config.NumberColumn(format="%d", help="Current live Steam follower count"),
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
        st.info("No Steam releases currently within the selected cutoff window.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # TABLE DIVISION 2: CONSOLE EXCLUSIVE TRACKS
    # -------------------------------------------------------------------------
    st.subheader("🎮 Console Exclusive / First Tracks")
    
    df_console = df[df["steam_id"] == 0].copy()
    if not df_console.empty:
        df_console = df_console.sort_values(by="OpenCritic Score", ascending=False, na_position="last")
        df_console = df_console[["Game Title", "Origin", "Release Date", "OpenCritic Score", "Metacritic Score"]]
        
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
        st.info("No Console-first exclusives currently within the selected cutoff window.")

    st.caption("Ecosystem Status: Active. Public presentation data synchronized.")