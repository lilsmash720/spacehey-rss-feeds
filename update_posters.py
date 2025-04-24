import os
import re
import requests
import feedparser

# Simkl credentials
SIMKL_CLIENT_ID = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
HEADERS = {"Content-Type": "application/json", "simkl-api-key": SIMKL_CLIENT_ID}

# RSS feed URLs
MOVIES_RSS = "https://api.simkl.com/feeds/list/movies/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
TV_RSS = "https://api.simkl.com/feeds/list/tv/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"

POSTER_DIR = "posters"
os.makedirs(POSTER_DIR, exist_ok=True)

def parse_simkl_rss(feed_url, count=6):
    feed = feedparser.parse(feed_url)
    results = []

    for entry in feed.entries:
        match = re.search(r"/(movies|tv)/(\d+)", entry.link)
        if match:
            media_type = match.group(1)
            simkl_id = match.group(2)
            results.append((media_type, simkl_id))
        if len(results) >= count:
            break

    return results

def get_simkl_poster_url(media_type, simkl_id):
    endpoint = f"https://api.simkl.com/{'movies' if media_type == 'movies' else 'shows'}/{simkl_id}"
    res = requests.get(endpoint, headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ Simkl API error for ID {simkl_id}: {res.status_code}")
        return None
    data = res.json()
    poster = data.get("poster", {})
    return poster.get("poster_xl") or poster.get("poster")

def download_poster(url, filename):
    if not url:
        print(f"❌ No poster URL for {filename}")
        return
    try:
        res = requests.get(url)
        if res.status_code == 200:
            with open(os.path.join(POSTER_DIR, filename), "wb") as f:
                f.write(res.content)
            print(f"✅ Downloaded {filename}")
        else:
            print(f"❌ Failed to download {filename} (HTTP {res.status_code})")
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")

def update_posters():
    print("🎬 Updating movie posters...")
    movies = parse_simkl_rss(MOVIES_RSS)
    for i, (media_type, simkl_id) in enumerate(movies, 1):
        poster_url = get_simkl_poster_url(media_type, simkl_id)
        download_poster(poster_url, f"movie{i}.jpg")

    print("\n📺 Updating TV show posters...")
    shows = parse_simkl_rss(TV_RSS)
    for i, (media_type, simkl_id) in enumerate(shows, 1):
        poster_url = get_simkl_poster_url(media_type, simkl_id)
        download_poster(poster_url, f"show{i}.jpg")

if __name__ == "__main__":
    update_posters()


