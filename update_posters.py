import os
import requests
from pathlib import Path
import re

# --- Config ---
SIMKL_API_KEY = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
USER_ID = "7233116"
POSTER_DIR = Path("posters")
POSTER_DIR.mkdir(exist_ok=True)

headers = {
    "simkl-api-key": SIMKL_API_KEY,
    "Accept": "application/json"
}

def sanitize_filename(name):
    """Remove special characters from filenames"""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def fetch_items(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Handle different response structures
        if "movies" in data:  # For movies response
            return data["movies"][:6]
        if "shows" in data:  # For shows response
            return data["shows"][:6]
        return data[:6]  # Fallback
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def get_poster_url(item):
    # Handle different media types
    media = item.get("movie") or item.get("show") or {}
    posters = media.get("poster") or {}
    
    # Prioritize TMDB images if available
    return posters.get("tmdb", {}).get("full") or posters.get("full")

def download_poster(url, filename):
    if not url:
        print(f"No poster available for {filename}")
        return False
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(POSTER_DIR / filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
        return False

def main():
    print("Fetching media from Simkl...")

    # Updated API endpoints
    movie_url = f"https://api.simkl.com/movies/watched/{USER_ID}"
    show_url = f"https://api.simkl.com/shows/watching/{USER_ID}"

    movies = fetch_items(movie_url)
    shows = fetch_items(show_url)

    for i, item in enumerate(movies + shows, 1):
        media_type = "movie" if "movie" in item else "show"
        title = item[media_type].get("title", f"unknown_{i}")
        safe_title = sanitize_filename(title)[:50]  # Limit filename length
        poster_url = get_poster_url(item)
        
        ext = "jpg"  # Most posters are JPEGs
        if poster_url and "webp" in poster_url:
            ext = "webp"
            
        filename = f"{media_type}_{safe_title}_{i}.{ext}"
        download_poster(poster_url, filename)

    print("Process completed. Check the 'posters' directory.")

if __name__ == "__main__":
    main()
