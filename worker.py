import json
import time
import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup
import game_database as gd

METRICS_FILE = "metrics.json"
TIMEOUT = 10
DELAY_BETWEEN_GAMES = 2

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

def parse_date(date_str):
    if not date_str or date_str == "2099-01-01":
        return None
    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%d %b, %Y", "%B %d, %Y", "%d %B, %Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def load_existing_metrics():
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_metrics(data):
    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def fetch_game_data(game_name, config, existing_data):
    appid = config["steam_id"]
    
    # Pre-populate defaults or retain previous state
    game_record = existing_data.get(game_name, {
        "all_time_peak": config["backup_peak"],
        "release_date": "2099-01-01",
        "live_ccu": "N/A",
        "steam_rating": "N/A",
        "total_reviews": "N/A",
        "opencritic_score": "N/A",
        "metacritic_score": "N/A",
        "tags": "—"
    })

    # 1. Fetch Live CCU
    live_ccu = "N/A"
    if appid:
        url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
        try:
            res = requests.get(url, headers=BASE_HEADERS, timeout=TIMEOUT)
            if res.status_code == 200:
                live_ccu = res.json().get("response", {}).get("player_count", "N/A")
        except Exception:
            pass

    # 2. Local State Tracker for Peaks
    if isinstance(live_ccu, int):
        current_peak = game_record.get("all_time_peak", config["backup_peak"])
        if live_ccu > current_peak:
            game_record["all_time_peak"] = live_ccu
    game_record["live_ccu"] = live_ccu

    # 3. Fetch Storefront Release Date (ONLY IF UNRELEASED)
    current_rd = config.get("release_date") or game_record.get("release_date", "2099-01-01")
    is_released = False
    if current_rd and current_rd != "2099-01-01":
        parsed_dt = parse_date(current_rd)
        if parsed_dt and parsed_dt <= datetime.now():
            is_released = True

    if appid and not is_released:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=english"
        try:
            res = requests.get(url, headers=BASE_HEADERS, timeout=TIMEOUT)
            if res.status_code == 200 and res.json().get(str(appid), {}).get("success"):
                rd = res.json()[str(appid)]["data"]["release_date"]
                if rd.get("coming_soon"):
                    game_record["release_date"] = "2099-01-01"
                else:
                    new_rd_date = rd.get("date", game_record["release_date"])
                    if new_rd_date != game_record["release_date"]:
                        print(f"  -> {game_name} release date shifted to: {new_rd_date}")
                        game_record["release_date"] = new_rd_date
        except Exception:
            pass

    # 💡 3.5 Fetch Steam Community Tags (Bypassing Mature Content Age Gates)
    # Uses persistent browser bypass state parameters during execution loops
    if appid and game_record.get("tags", "—") in ("—", "N/A", ""):
        url = f"https://store.steampowered.com/app/{appid}/"
        
        # 💡 FIX: Injecting standard age-verification session markers
        steam_age_bypass_cookies = {
            "wants_mature_content": "1",
            "lastagecheckage": "1-1-1990",
            "birthtime": "631180801"
        }
        
        try:
            res = requests.get(
                url, 
                headers=BASE_HEADERS, 
                cookies=steam_age_bypass_cookies, 
                timeout=TIMEOUT
            )
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                tag_elements = soup.find_all("a", class_="app_tag")
                # Parse text, filter out blanks, and grab the top 3 popular tags
                tags_list = [t.get_text(strip=True) for t in tag_elements if t.get_text(strip=True)][:3]
                if tags_list:
                    game_record["tags"] = ", ".join(tags_list)
        except Exception:
            pass

    # 4. Fetch Steam Storefront Reviews
    if appid:
        url = f"https://store.steampowered.com/appreviews/{appid}?json=1&language=all&purchase_type=all"
        try:
            res = requests.get(url, headers=BASE_HEADERS, timeout=TIMEOUT)
            if res.status_code == 200:
                summary = res.json().get("query_summary", {})
                tot = summary.get("total_reviews", 0)
                pos = summary.get("total_positive", 0)
                if tot > 0:
                    game_record["steam_rating"] = round((pos / tot) * 100, 2)
                    game_record["total_reviews"] = tot
        except Exception:
            pass

    # 5. Fetch OpenCritic Scores (Direct REST Endpoint)
    oc_id = config.get("opencritic_id")
    if oc_id and oc_id != 0:
        url = f"https://api.opencritic.com/api/game/{oc_id}"
        try:
            res = requests.get(url, headers=BASE_HEADERS, timeout=TIMEOUT)
            if res.status_code == 200:
                data = res.json()
                # OpenCritic provides topCriticScore as an int/float
                score = data.get("topCriticScore")
                if score and score > 0:
                    game_record["opencritic_score"] = int(round(score))
        except Exception:
            pass

    # 6. Fetch Metacritic Scores
    if config.get("metacritic_slug"):
        url = f"https://www.metacritic.com/game/{config['metacritic_slug']}/"
        try:
            res = requests.get(url, headers=BASE_HEADERS, timeout=TIMEOUT)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for tag in soup.find_all("script", type="application/ld+json"):
                    try:
                        data = json.loads(tag.string)
                        rating = data.get("aggregateRating", {}).get("ratingValue")
                        if rating:
                            game_record["metacritic_score"] = int(float(rating))
                            break
                    except Exception:
                        continue
        except Exception:
            pass

    return game_record

def main():
    existing_data = load_existing_metrics()
    updated_data = {}
    
    for game_name, config in gd.GAME_DATABASE.items():
        print(f"Polling update cycle for {game_name}...")
        updated_data[game_name] = fetch_game_data(game_name, config, existing_data)
        time.sleep(DELAY_BETWEEN_GAMES)
        
    save_metrics(updated_data)
    print("Metrics snapshot successfully updated.")

if __name__ == "__main__":
    main()