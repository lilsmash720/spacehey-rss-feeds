import os
import re
import requests
import feedparser

# === CONFIG ===
SIMKL_CLIENT_ID = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
TMDB_API_KEY = "08d2466ce60a24dce25b03cc1ae3f497"
HEADERS = {"Authorization": f"Bearer {TMDB_API_KEY}"}

MOVIES_RSS = "https://api.simkl.com/feeds/list/movies/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
TV_RSS = "https://api.simkl.com/feeds/list/tv/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
POSTER_DIR = "posters"

os.makedirs(POSTER_DIR, exist_ok=True)

def extract_simkl_ids(feed_url, type_, count=6):
    feed = feedparser.parse(feed_url)
    simkl_ids = []
    for entry in feed.entries[:count]:
        match = re.search(rf"/{type_}/(\d+)", entry.link)
        if match:
            simkl_ids.append(match.group(1))
    return simkl_ids

def get_tmdb_id_from_simkl(simkl_type, simkl_id):
    url = f"https://api.simkl.com/{simkl_type}s/{simkl_id}?extended=full"
    headers = {"simkl-api-key": SIMKL_CLIENT_ID}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"❌ Simkl API error for {simkl_type} ID {simkl_id}: {res.status_code}")
        return None
    data = res.json()
    return data.get("ids", {}).get("tmdb")

def get_poster_path(tmdb_id, type_):
    url = f"https://api.themoviedb.org/3/{type_}/{tmdb_id}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return None
    return res.json().get("poster_path")

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
    print("\n🎬 Updating movie posters...")
    movie_ids = extract_simkl_ids(MOVIES_RSS, "movies")
    for i, simkl_id in enumerate(movie_ids, start=1):
        tmdb_id = get_tmdb_id_from_simkl("movie", simkl_id)
        poster_path = get_poster_path(tmdb_id, "movie") if tmdb_id else None
        download_poster(poster_path, f"movie{i}.jpg")

    print("\n📺 Updating TV show posters...")
    show_ids = extract_simkl_ids(TV_RSS, "tv")
    for i, simkl_id in enumerate(show_ids, start=1):
        tmdb_id = get_tmdb_id_from_simkl("show", simkl_id)
        poster_path = get_poster_path(tmdb_id, "tv") if tmdb_id else None
        download_poster(poster_path, f"show{i}.jpg")

if __name__ == "__main__":
    update_posters()
