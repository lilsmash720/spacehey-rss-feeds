import os
import requests
import feedparser
import re

TMDB_API_KEY = "08d2466ce60a24dce25b03cc1ae3f497"
HEADERS = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOGQyNDY2Y2U2MGEyNGRjZTI1YjAzY2MxYWUzZjQ5NyIsIm5iZiI6MTczNDEyMDA0OC44NjcsInN1YiI6IjY3NWM5MjcwMzA3OTY0ZDAyMGIzNzFmMiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ._gn3ltr__2hOSgecNgffiHosTwg_sAMVU1W3GP6w8BY"}

MOVIES_RSS = "https://api.simkl.com/feeds/list/movies/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
TV_RSS = "https://api.simkl.com/feeds/list/tv/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
POSTER_DIR = "posters"

os.makedirs(POSTER_DIR, exist_ok=True)

def extract_tmdb_ids(feed_url, count=6):
    feed = feedparser.parse(feed_url)
    ids = []
    for entry in feed.entries:
        # Look for tmdb:id format anywhere in the entry fields
        for value in entry.values():
            if isinstance(value, str):
                match = re.search(r"tmdb[:_](\d+)", value, re.IGNORECASE)
                if match:
                    ids.append(match.group(1))
                    break
        if len(ids) >= count:
            break
    return ids

def get_poster_path(tmdb_id, type_):
    url = f"https://api.themoviedb.org/3/{type_}/{tmdb_id}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ TMDb API error for ID {tmdb_id}: {res.status_code}")
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
    movie_ids = extract_tmdb_ids(MOVIES_RSS)
    show_ids = extract_tmdb_ids(TV_RSS)

    print("\n🎬 Movie TMDb IDs:", movie_ids)
    for i, tmdb_id in enumerate(movie_ids, 1):
        poster = get_poster_path(tmdb_id, "movie")
        download_poster(poster, f"movie{i}.jpg")

    print("\n📺 TV Show TMDb IDs:", show_ids)
    for i, tmdb_id in enumerate(show_ids, 1):
        poster = get_poster_path(tmdb_id, "tv")
        download_poster(poster, f"show{i}.jpg")

if __name__ == "__main__":
    update_posters()

