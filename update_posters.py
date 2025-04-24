import os
import requests
from urllib.parse import urljoin
from pathlib import Path

# --- Config ---
SIMKL_API_KEY = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
USER_ID = "7233116"
HEADERS = {"simkl-api-key": SIMKL_API_KEY}
POSTER_DIR = Path("posters")
POSTER_DIR.mkdir(exist_ok=True)

def fetch_items(endpoint):
    response = requests.get(endpoint, headers=HEADERS)
    response.raise_for_status()
    return response.json()[:6]

def get_poster_url(item):
    ids = item.get("ids", {})
    simkl_id = ids.get("simkl")
    if not simkl_id:
        return None

    media_type = item.get("type", "movie")
    if media_type == "movie":
        path = f"/movies/{simkl_id}"
    else:
        path = f"/shows/{simkl_id}"

    detail_url = f"https://api.simkl.com{path}?extended=full"
    res = requests.get(detail_url, headers=HEADERS)
    res.raise_for_status()
    data = res.json()

    images = data.get("images", {})
    return images.get("poster", {}).get("full")

def download_poster(url, filename):
    if not url:
        print(f"Poster not found for {filename}")
        return
    response = requests.get(url)
    response.raise_for_status()
    with open(POSTER_DIR / filename, "wb") as f:
        f.write(response.content)
    print(f"Saved poster: {filename}")

def main():
    print("Fetching recent movies and TV shows from Simkl...")

    movie_endpoint = f"https://api.simkl.com/history/movies/all/{USER_ID}?limit=6&extended=full"
    show_endpoint = f"https://api.simkl.com/history/shows/{USER_ID}?limit=6&extended=full"

    recent_movies = fetch_items(movie_endpoint)
    recent_shows = fetch_items(show_endpoint)

    for i, movie in enumerate(recent_movies, 1):
        poster_url = get_poster_url({**movie, "type": "movie"})
        download_poster(poster_url, f"movie{i}.jpg")

    for i, show in enumerate(recent_shows, 1):
        poster_url = get_poster_url({**show, "type": "show"})
        download_poster(poster_url, f"show{i}.jpg")

    print("Done!")

if __name__ == "__main__":
    main()

