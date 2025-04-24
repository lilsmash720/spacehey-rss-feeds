import os
import requests
from pathlib import Path

# --- Config ---
SIMKL_API_KEY = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
USERNAME = "7233116"
POSTER_DIR = Path("posters")
POSTER_DIR.mkdir(exist_ok=True)

def fetch_items(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()[:6]

def get_poster_url(item):
    images = item.get("poster", {})
    return images.get("full")

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

    movie_url = f"https://api.simkl.com/movies/list/completed/{USERNAME}?client_id={SIMKL_API_KEY}"
    show_url = f"https://api.simkl.com/shows/list/watching/{USERNAME}?client_id={SIMKL_API_KEY}"

    recent_movies = fetch_items(movie_url)
    recent_shows = fetch_items(show_url)

    for i, movie in enumerate(recent_movies, 1):
        poster_url = get_poster_url(movie)
        download_poster(poster_url, f"movie{i}.jpg")

    for i, show in enumerate(recent_shows, 1):
        poster_url = get_poster_url(show)
        download_poster(poster_url, f"show{i}.jpg")

    print("Done!")

if __name__ == "__main__":
    main()


