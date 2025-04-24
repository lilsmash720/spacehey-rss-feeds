import requests
import os

# Simkl API key from your environment variable
SIMKL_CLIENT_ID = os.getenv("SIMKL_CLIENT_ID")

# TMDb API key (hardcoded here, but use env vars for production)
TMDB_API_KEY = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"

# Simkl endpoints
SIMKL_RECENT_MOVIES_URL = "https://api.simkl.com/history/movies/all/recent"
SIMKL_RECENT_SHOWS_URL = "https://api.simkl.com/history/shows/all/recent"

# TMDb poster base URL
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"

HEADERS = {
    "Content-Type": "application/json",
    "simkl-api-key": SIMKL_CLIENT_ID
}

def fetch_recent_items(url, item_type):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    items = []
    for entry in data:
        item = entry.get(item_type)
        if not item:
            continue

        ids = item.get('ids', {})
        tmdb_id = ids.get('tmdb')
        if tmdb_id:
            items.append({
                "title": item.get("title", "Unknown"),
                "tmdb_id": tmdb_id
            })
        if len(items) >= 6:
            break

    return items

def get_poster_urls(items, media_type):
    urls = []
    for item in items:
        tmdb_id = item["tmdb_id"]
        tmdb_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}"
        try:
            r = requests.get(tmdb_url)
            r.raise_for_status()
            poster_path = r.json().get("poster_path")
            if poster_path:
                urls.append(f"{TMDB_IMAGE_BASE_URL}{poster_path}")
        except Exception as e:
            print(f"Failed to fetch poster for {item['title']} ({tmdb_id}): {e}")
    return urls

def download_poster(url, filename):
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def download_posters(movie_posters, show_posters):
    for i, url in enumerate(movie_posters[:6], 1):
        download_poster(url, f"movie{i}.jpg")
    for i, url in enumerate(show_posters[:6], 1):
        download_poster(url, f"show{i}.jpg")

def main():
    print("Fetching recent movies and shows from Simkl...")
    recent_movies = fetch_recent_items(SIMKL_RECENT_MOVIES_URL, "movie")
    recent_shows = fetch_recent_items(SIMKL_RECENT_SHOWS_URL, "show")

    print("Fetching poster URLs from TMDb...")
    movie_posters = get_poster_urls(recent_movies, "movie")
    show_posters = get_poster_urls(recent_shows, "tv")

    print("Downloading posters...")
    download_posters(movie_posters, show_posters)

if __name__ == "__main__":
    main()

