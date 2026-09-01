import json
import time
import requests
import os
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import game_database as gd

METRICS_FILE = "metrics.json"
TIMEOUT = 12
DELAY_BETWEEN_GAMES = 1.5

# Follower Batch Settings
MAX_FOLLOWER_CHECKS_PER_RUN = 8  # Safe budget per execution run
FOLLOWER_TTL_HOURS = 20          # Re-fetch after 20 hours

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
})
session.cookies.update({
    "wants_mature_content": "1",
    "lastagecheckage": "1-1-1990",
    "birthtime": "631180801"
})

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

def select_games_for_follower_check(database, existing_data):
    candidates = []
    now = datetime.now()

    for game_name, config in database.items():
        appid = config.get("steam_id", 0)
        if not appid:
            continue

        record = existing_data.get(game_name, {})
        last_updated_str = record.get("followers_last_updated")
        current_followers = record.get("followers_current")

        if current_followers in (None, "N/A", "—") or not last_updated_str:
            candidates.append((game_name, datetime.min))
            continue

        try:
            last_dt = datetime.fromisoformat(last_updated_str)
            if now - last_dt >= timedelta(hours=FOLLOWER_TTL_HOURS):
                candidates.append((game_name, last_dt))
        except ValueError:
            candidates.append((game_name, datetime.min))

    candidates.sort(key=lambda x: x[1])
    return set(name for name, _ in candidates[:MAX_FOLLOWER_CHECKS_PER_RUN])

def fetch_game_data(game_name, config, existing_data, fetch_followers=False):
    appid = config["steam_id"]
    
    # Pre-populate defaults and guarantee all keys exist
    game_record = existing_data.get(game_name, {})
    game_record.setdefault("all_time_peak", config["backup_peak"])
    game_record.setdefault("release_date", "2099-01-01")
    game_record.setdefault("live_ccu", "N/A")
    game_record.setdefault("steam_rating", "N/A")
    game_record.setdefault("total_reviews", "N/A")
    game_record.setdefault("opencritic_score", "N/A")
    game_record.setdefault("metacritic_score", "N/A")
    game_record.setdefault("price_current_eur", game_record.get("price_eur", "N/A"))
    game_record.setdefault("price_release_eur", game_record.get("price_eur", "N/A"))
    game_record.setdefault("discount_release_pct", game_record.get("discount_pct", 0))
    game_record.setdefault("followers_initial", "N/A")
    game_record.setdefault("followers_release", "N/A")
    game_record.setdefault("followers_current", "N/A")
    game_record.setdefault("followers_last_updated", None)
    game_record.setdefault("tags", "—")

    # 1. Fetch Live CCU
    live_ccu = "N/A"
    if appid:
        url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
        try:
            res = session.get(url, timeout=TIMEOUT)
            if res.status_code == 200:
                live_ccu = res.json().get("response", {}).get("player_count", "N/A")
        except Exception:
            pass

    # 2. Local State Tracker for Peaks
    if isinstance(live_ccu, int):
        current_peak = game_record.get("all_time_peak", config["backup_peak"])
        if isinstance(current_peak, int):
            if live_ccu > current_peak:
                game_record["all_time_peak"] = live_ccu
        else:
            game_record["all_time_peak"] = live_ccu
    game_record["live_ccu"] = live_ccu

    # 3. Determine Release Status
    current_rd = config.get("release_date") or game_record.get("release_date", "2099-01-01")
    is_released = False
    if current_rd and current_rd != "2099-01-01":
        parsed_dt = parse_date(current_rd)
        if parsed_dt and parsed_dt <= datetime.now():
            is_released = True

    # 4. Fetch Storefront Details (Price in EUR, Release Date, & Release Discount)
    if appid:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=DE&l=english"
        try:
            res = session.get(url, timeout=TIMEOUT)
            if res.status_code == 200 and res.json().get(str(appid), {}).get("success"):
                app_data = res.json()[str(appid)]["data"]
                
                if app_data.get("is_free"):
                    game_record["price_current_eur"] = 0.0
                    game_record["price_release_eur"] = 0.0
                    game_record["discount_release_pct"] = 0
                elif "price_overview" in app_data:
                    po = app_data["price_overview"]
                    final_price = round(po.get("final", 0) / 100.0, 2)
                    initial_price = round(po.get("initial", 0) / 100.0, 2)
                    disc_pct = po.get("discount_percent", 0)
                    
                    game_record["price_current_eur"] = final_price

                    # Record release price baseline
                    if game_record.get("price_release_eur") in (None, "N/A", "—"):
                        game_record["price_release_eur"] = initial_price if initial_price > 0 else final_price

                    # Lock in release discount: update freely while unreleased, freeze once released
                    if not is_released:
                        game_record["discount_release_pct"] = disc_pct
                    else:
                        if game_record.get("discount_release_pct") in (None, "N/A", "—"):
                            game_record["discount_release_pct"] = disc_pct

                if not is_released:
                    rd = app_data.get("release_date", {})
                    if rd.get("coming_soon"):
                        game_record["release_date"] = "2099-01-01"
                    else:
                        new_rd_date = rd.get("date", game_record["release_date"])
                        if new_rd_date != game_record["release_date"]:
                            print(f"  -> {game_name} release date shifted to: {new_rd_date}")
                            game_record["release_date"] = new_rd_date
        except Exception:
            pass

    # 5. Fetch Steam Followers (Batch-managed)
    if appid and fetch_followers:
        followers_count = None
        xml_url = f"https://steamcommunity.com/games/{appid}/memberslistxml/?xml=1"
        
        try:
            res = session.get(xml_url, timeout=TIMEOUT)
            if res.status_code == 200:
                match = re.search(r'<memberCount>\s*([0-9,]+)\s*</memberCount>', res.text)
                if match:
                    followers_count = int(match.group(1).replace(",", ""))
            elif res.status_code == 429:
                print(f"  [!] Rate limited on followers for {game_name}. Will retry next scheduled run.")
        except Exception:
            pass

        if followers_count is None:
            hub_url = f"https://steamcommunity.com/app/{appid}"
            try:
                res = session.get(hub_url, timeout=TIMEOUT)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    elem = soup.find(class_=re.compile(r"apphub_NumInGroup|apphub_NumMembers"))
                    if elem:
                        match = re.search(r'([0-9,]+)', elem.get_text())
                        if match:
                            followers_count = int(match.group(1).replace(",", ""))
            except Exception:
                pass

        if followers_count is not None:
            game_record["followers_current"] = followers_count
            game_record["followers_last_updated"] = datetime.now().isoformat()
            print(f"  -> [Followers Updated] {game_name}: {followers_count:,}")
            
            if game_record.get("followers_initial") in (None, "N/A", 0, "—"):
                game_record["followers_initial"] = followers_count
                
            if is_released and game_record.get("followers_release") in (None, "N/A", 0, "—"):
                game_record["followers_release"] = followers_count
        
        time.sleep(3.0)

    # 6. Fetch Steam Community Tags
    if appid and game_record.get("tags", "—") in ("—", "N/A", ""):
        url = f"https://store.steampowered.com/app/{appid}/"
        try:
            res = session.get(url, timeout=TIMEOUT)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                tag_elements = soup.find_all("a", class_="app_tag")
                tags_list = [t.get_text(strip=True) for t in tag_elements if t.get_text(strip=True)][:3]
                if tags_list:
                    game_record["tags"] = ", ".join(tags_list)
        except Exception:
            pass

    # 7. Fetch Steam Storefront Reviews
    if appid:
        url = f"https://store.steampowered.com/appreviews/{appid}?json=1&language=all&purchase_type=all"
        try:
            res = session.get(url, timeout=TIMEOUT)
            if res.status_code == 200:
                summary = res.json().get("query_summary", {})
                tot = summary.get("total_reviews", 0)
                pos = summary.get("total_positive", 0)
                if tot > 0:
                    game_record["steam_rating"] = round((pos / tot) * 100, 2)
                    game_record["total_reviews"] = tot
        except Exception:
            pass

    # 8. Fetch OpenCritic Scores
    oc_id = config.get("opencritic_id")
    oc_slug = config.get("opencritic_slug")
    if oc_id and oc_id != 0:
        score_val = None
        urls_to_try = []
        if oc_slug:
            urls_to_try.append(f"https://opencritic.com/game/{oc_id}/{oc_slug}")
        urls_to_try.append(f"https://opencritic.com/game/{oc_id}")

        for target_url in urls_to_try:
            try:
                res = requests.get(target_url, headers=session.headers, timeout=TIMEOUT)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    orb_elem = soup.find(class_=re.compile(r"inner-orb|score-orb|score-number"))
                    if orb_elem and orb_elem.get_text(strip=True).isdigit():
                        score_val = int(orb_elem.get_text(strip=True))
                        break

                    text_content = soup.get_text()
                    match_text = re.search(r'([0-9]{1,3})\s*(?:\.?|\s*)\s*Top Critic Average', text_content, re.IGNORECASE)
                    if match_text:
                        score_val = int(match_text.group(1))
                        break

                    meta_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
                    if meta_desc and meta_desc.get("content"):
                        match_meta = re.search(r'top critic average of\s*([0-9]{1,3})', meta_desc["content"], re.IGNORECASE)
                        if match_meta:
                            score_val = int(match_meta.group(1))
                            break
            except Exception:
                pass

        if score_val and score_val > 0:
            game_record["opencritic_score"] = score_val

    # 9. Fetch Metacritic Scores
    if config.get("metacritic_slug"):
        url = f"https://www.metacritic.com/game/{config['metacritic_slug']}/"
        try:
            res = requests.get(url, headers=session.headers, timeout=TIMEOUT)
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
    
    follower_targets = select_games_for_follower_check(gd.GAME_DATABASE, existing_data)
    print(f"Scheduled {len(follower_targets)} games for follower updates in this run: {list(follower_targets)}")
    
    for game_name, config in gd.GAME_DATABASE.items():
        print(f"Polling update cycle for {game_name}...")
        should_check_followers = game_name in follower_targets
        updated_data[game_name] = fetch_game_data(
            game_name, 
            config, 
            existing_data, 
            fetch_followers=should_check_followers
        )
        time.sleep(DELAY_BETWEEN_GAMES)
        
    save_metrics(updated_data)
    print("Metrics snapshot successfully updated.")

if __name__ == "__main__":
    main()