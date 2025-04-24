import os
import requests

SIMKL_CLIENT_ID = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
HEADERS = {
    "Content-Type": "application/json",
    "simkl-api-key": SIMKL_CLIENT_ID
}

POSTER_DIR = "posters"
os.makedirs(POSTER_DIR, exist_ok=True)

def fetch_simkl_history(media_type, limit=6):
    url = f"https://api.simkl.com/history/{media_type}/completed?limit={limit}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ Failed to fetch {media_type}: {res.status_code}")
        return []
    return res.json()

def get_poster_url(item):
    if 'poster' in item and item['poster']:
        return f"https://simkl.in/posters/{item['poster']}_w500.jpg"
    return None

def download_poster(url, filename):
    if not url:
        print(f"❌ No poster URL for {filename}")
        return
    try:
        img_data = requests.get(url).content
        with open(os.path.join(POSTER_DIR, filename), "wb") as f:
            f.write(img_data)
        print(f"✅ Downloaded {filename}")
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")

def update_posters():
    print("🎬 Updating movie posters...")
    movies = fetch_simkl_history("movies")
    for i, item in enumerate(movies, 1):
        url = get_poster_url(item.get("movie", {}))
        download_poster(url, f"movie{i}.jpg")

    print("\n📺 Updating TV show posters...")
    shows = fetch_simkl_history("shows")
    for i, item in enumerate(shows, 1):
        url = get_poster_url(item.get("show", {}))
        download_poster(url, f"show{i}.jpg")

if __name__ == "__main__":
    update_posters()

