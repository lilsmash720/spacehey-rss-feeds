import os
import re
import requests
import feedparser

# === CONFIG ===
SIMKL_CLIENT_ID = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
TMDB_API_KEY = "08d2466ce60a24dce25b03cc1ae3f497"

MOVIES_RSS = "https://api.simkl.com/feeds/list/movies/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
TV_RSS = "https://api.simkl.com/feeds/list/tv/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
POSTER_DIR = "posters"

os.makedirs(POSTER_DIR, exist_ok=True)

def extract_simkl_ids(feed_url, type_, count=6):
    feed = feedparser.parse(feed_url)
    simkl_ids = []
    print(f"Parsing {type_} RSS feed...")
    for entry in feed.entries[:count]:
        print(f"Link found in entry: {entry.link}")  # Print the full link for inspection
        if type_ == "tv":
            # Support both "shows" and "tv" formats
            match = re.search(r"/(tv|shows)/(\d+)", entry.link)
        else:
            match = re.search(rf"/{type_}/(\d+)", entry.link)
        
        if match:
            simkl_ids.append(match.group(2))  # Capture the ID (group 2 after the type)
        else:
            print(f"❌ No {type_} ID found in entry: {entry.link}")
    print(f"Found {len(simkl_ids)} {type_} IDs.")
    return simkl_ids

def get_tmdb_id_from_simkl(simkl_type, simkl_id):
    url = f"https://api.simkl.com/{simkl_type}s/{simkl_id}?extended=full"
    headers = {"simkl-api-key": SIMKL_CLIENT_ID}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"❌ Simkl API error for {simkl_type} ID {simkl_id}: {res.status_code}")
        return None
    data = res.json()
    tmdb_id = data.get("ids", {}).get("tmdb")
    print(f"🎯 Simkl ID {simkl_id} ➡️ TMDb ID: {tmdb_id}")
    return tmdb_id

def get_poster_path(tmdb_id, type_):
    print(f"🎬 Fetching poster from TMDb for {type_} ID {tmdb_id}")
    url = f"https://api.themoviedb.org/3/{type_}/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,  # Use the API key as a query parameter
        "language": "en-US"
    }
    res = requests.get(url, params=params)  # Pass params directly to the request
    if res.status_code != 200:
        print(f"❌ TMDb error for {type_} ID {tmdb_id}: {res.status_code}")
        return None
    poster_path = res.json().get("poster_path")
    print(f"🖼️ Poster path for {type_} ID {tmdb_id}: {poster_path}")
    return poster_path

def download_poster(poster_path, filename):
    if not poster_path:
        print(f"❌ No poster path for {filename}")
        return
    url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    img_data = requests.get(url).content
    with open(os.path.join(POSTER_DIR, filename), "wb") as f:
        f.write(img_data)
    print(f"✅ Downloaded {filename}")

def update_posters():
    print("\n🎬 Updating most recent movie posters...")
    movie_ids = extract_simkl_ids(MOVIES_RSS, "movies")
    for i, simkl_id in enumerate(movie_ids, start=1):
        tmdb_id = get_tmdb_id_from_simkl("movie", simkl_id)
        poster_path = get_poster_path(tmdb_id, "movie") if tmdb_id else None
        download_poster(poster_path, f"movie{i}.jpg")

    print("\n📺 Updating most recent TV show posters...")
    show_ids = extract_simkl_ids(TV_RSS, "tv")
    if not show_ids:
        print("❌ No TV show IDs found. Check the RSS feed or filter settings.")
    for i, simkl_id in enumerate(show_ids, start=1):
        tmdb_id = get_tmdb_id_from_simkl("show", simkl_id)
        poster_path = get_poster_path(tmdb_id, "tv") if tmdb_id else None
        download_poster(poster_path, f"show{i}.jpg")

if __name__ == "__main__":
    update_posters()
