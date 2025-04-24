import os
import re
import requests
import feedparser

# RSS feed URLs
MOVIES_RSS = "https://api.simkl.com/feeds/list/movies/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
TV_RSS = "https://api.simkl.com/feeds/list/tv/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"

POSTER_DIR = "posters"
os.makedirs(POSTER_DIR, exist_ok=True)

def parse_simkl_rss(feed_url, media_type, count=6):
    feed = feedparser.parse(feed_url)
    results = []

    for entry in feed.entries:
        # Extract Simkl ID from the URL
        match = re.search(r"/(movies|tv)/(\d+)/", entry.link)
        if match:
            type_from_link = match.group(1)
            simkl_id = match.group(2)
            results.append((type_from_link, simkl_id))
        if len(results) >= count:
            break

    return results

def get_poster_url(media_type, simkl_id):
    return f"https://simkl.in/posters/{media_type}/{simkl_id}_w500.jpg"

def download_poster(url, filename):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            with open(os.path.join(POSTER_DIR, filename), "wb") as f:
                f.write(res.content)
            print(f"✅ Downloaded {filename}")
        else:
            print(f"❌ Poster not found for {filename} (HTTP {res.status_code})")
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")

def update_posters():
    print("🎬 Updating movie posters...")
    movies = parse_simkl_rss(MOVIES_RSS, "movies")
    for i, (media_type, simkl_id) in enumerate(movies, 1):
        poster_url = get_poster_url(media_type, simkl_id)
        download_poster(poster_url, f"movie{i}.jpg")

    print("\n📺 Updating TV show posters...")
    shows = parse_simkl_rss(TV_RSS, "tv")
    for i, (media_type, simkl_id) in enumerate(shows, 1):
        poster_url = get_poster_url(media_type, simkl_id)
        download_poster(poster_url, f"show{i}.jpg")

if __name__ == "__main__":
    update_posters()


