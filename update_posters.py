import os
import re
import feedparser
import requests

MOVIES_RSS = "https://api.simkl.com/feeds/list/movies/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
TV_RSS = "https://api.simkl.com/feeds/list/tv/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
POSTER_DIR = "posters"
os.makedirs(POSTER_DIR, exist_ok=True)

def extract_simkl_ids(feed_url, type_, count=6):
    feed = feedparser.parse(feed_url)
    ids = []
    for entry in feed.entries:
        match = re.search(rf"{type_}/(\d+)", entry.link)
        if match:
            ids.append(match.group(1))
        if len(ids) >= count:
            break
    return ids

def download_simkl_poster(simkl_id, filename):
    url = f"https://simkl.in/posters/{simkl_id}/poster_xl.jpg"
    res = requests.get(url)
    if res.status_code == 200:
        with open(os.path.join(POSTER_DIR, filename), "wb") as f:
            f.write(res.content)
        print(f"✅ Downloaded {filename}")
    else:
        print(f"❌ No poster URL for {filename}")

def update_posters():
    print("\n🎬 Updating movie posters...")
    movie_ids = extract_simkl_ids(MOVIES_RSS, "movies")
    for i, simkl_id in enumerate(movie_ids, 1):
        download_simkl_poster(simkl_id, f"movie{i}.jpg")

    print("\n📺 Updating TV show posters...")
    show_ids = extract_simkl_ids(TV_RSS, "tv")
    for i, simkl_id in enumerate(show_ids, 1):
        download_simkl_poster(simkl_id, f"show{i}.jpg")

if __name__ == "__main__":
    update_posters()


