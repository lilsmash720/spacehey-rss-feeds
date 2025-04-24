import requests
from pathlib import Path
import re

# --- Config ---
CLIENT_ID = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
USER_ID = "7233116"
POSTER_DIR = Path("posters")
POSTER_DIR.mkdir(exist_ok=True)

headers = {
    "simkl-api-key": CLIENT_ID,
    "Accept": "application/json"
}

def sanitize_filename(name):
    """Remove special characters from filenames"""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def fetch_watched_media(media_type):
    base_url = f"https://api.simkl.com/sync/watched/{media_type}"
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"Debug - {media_type} response:", data)  # Keep for verification
        return data[:6]  # Return first 6 items
    except Exception as e:
        print(f"Error fetching {media_type}: {str(e)}")
        if response:  # Show error details if available
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
        return []

def get_poster_url(item):
    # Unified structure for movies/shows
    media = item.get("movie") or item.get("show") or {}
    return (media.get("poster") or 
            media.get("artwork") or 
            f"https://simkl.in/posters/{media.get('ids', {}).get('simkl')}_m.jpg")

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
    
    # Fetch watched movies and shows
    movies = fetch_watched_media("movies")
    shows = fetch_watched_media("shows")
    
    # Combine and process all media
    all_media = movies + shows
    if not all_media:
        print("No media found. Check your Simkl profile has watched content.")
        return

    for i, item in enumerate(all_media, 1):
        media_type = "movie" if "movie" in item else "show"
        title = item[media_type].get("title", f"media_{i}")
        year = item[media_type].get("year", "")
        safe_title = sanitize_filename(f"{title}_{year}")[:50]
        
        poster_url = get_poster_url(item)
        filename = f"{media_type}_{safe_title}_{i}.jpg"
        
        download_poster(poster_url, filename)

    print("Process completed. Check the 'posters' directory.")

if __name__ == "__main__":
    main()
