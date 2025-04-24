import os
import requests
import feedparser

# === CONFIG ===
TMDB_API_KEY = "08d2466ce60a24dce25b03cc1ae3f497"
HEADERS = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOGQyNDY2Y2U2MGEyNGRjZTI1YjAzY2MxYWUzZjQ5NyIsIm5iZiI6MTczNDEyMDA0OC44NjcsInN1YiI6IjY3NWM5MjcwMzA3OTY0ZDAyMGIzNzFmMiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ._gn3ltr__2hOSgecNgffiHosTwg_sAMVU1W3GP6w8BY"}

MOVIES_RSS = "https://api.simkl.com/feeds/list/movies/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
TV_RSS = "https://api.simkl.com/feeds/list/tv/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
POSTER_DIR = "posters"

os.makedirs(POSTER_DIR, exist_ok=True)

def fetch_titles(feed_url, count=6):
    feed = feedparser.parse(feed_url)
    return [entry.title for entry in feed.entries[:count]]

def search_tmdb(title, type_):
    url = f"https://api.themoviedb.org/3/search/{type_}"
    params = {"query": title, "api_key": TMDB_API_KEY}
    res = requests.get(url, params=params, headers=HEADERS)
    results = res.json().get("results", [])
    return results[0] if results else None

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
    movie_titles = fetch_titles(MOVIES_RSS)
    tv_titles = fetch_titles(TV_RSS)

    print("\n🎬 Updating movie posters...")
    for i, title in enumerate(movie_titles, start=1):
        result = search_tmdb(title, "movie")
        download_poster(result.get("poster_path") if result else None, f"movie{i}.jpg")

    print("\n📺 Updating TV show posters...")
    for i, title in enumerate(tv_titles, start=1):
        result = search_tmdb(title, "tv")
        download_poster(result.get("poster_path") if result else None, f"show{i}.jpg")

if __name__ == "__main__":
    update_posters()

