import os
import requests

# === CONFIG ===
SIMKL_CLIENT_ID = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
TMDB_API_KEY = "08d2466ce60a24dce25b03cc1ae3f497"
POSTER_DIR = "posters"

os.makedirs(POSTER_DIR, exist_ok=True)

# Fetch the latest movies and TV shows from Simkl
def fetch_simkl_data(type_, count=6):
    url = f"https://api.simkl.com/{type_}/trending"
    params = {"token": SIMKL_CLIENT_ID, "count": count}
    res = requests.get(url, params=params)
    if res.status_code != 200:
        print(f"❌ Simkl API error for {type_}: {res.status_code}")
        return []
    data = res.json()
    items = data.get(type_, [])
    print(f"Found {len(items)} {type_}s.")
    return items

# Get TMDb ID and IMDb ID from Simkl
def get_ids_from_simkl(simkl_type, simkl_id):
    url = f"https://api.simkl.com/{simkl_type}s/{simkl_id}?extended=full"
    headers = {"simkl-api-key": SIMKL_CLIENT_ID}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"❌ Simkl API error for {simkl_type} ID {simkl_id}: {res.status_code}")
        return None, None
    data = res.json()
    tmdb_id = data.get("ids", {}).get("tmdb")
    imdb_id = data.get("ids", {}).get("imdb")
    return tmdb_id, imdb_id

# Get poster path from TMDb
def get_poster_path(tmdb_id, type_):
    print(f"🎬 Fetching poster from TMDb for {type_} ID {tmdb_id}")
    url = f"https://api.themoviedb.org/3/{type_}/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        print(f"❌ TMDb error for {type_} ID {tmdb_id}: {res.status_code}")
        return None
    poster_path = res.json().get("poster_path")
    print(f"🖼️ Poster path for {type_} ID {tmdb_id}: {poster_path}")
    return poster_path

# Download poster image
def download_poster(poster_path, filename):
    if not poster_path:
        print(f"❌ No poster path for {filename}")
        return
    url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    img_data = requests.get(url).content
    with open(os.path.join(POSTER_DIR, filename), "wb") as f:
        f.write(img_data)
    print(f"✅ Downloaded {filename}")

# Main function to update posters
def update_posters():
    print("\n🎬 Updating most recent movie posters...")
    movie_items = fetch_simkl_data("movie", count=6)
    for i, item in enumerate(movie_items, start=1):
        simkl_id = item.get("id")
        tmdb_id, imdb_id = get_ids_from_simkl("movie", simkl_id)
        if not tmdb_id and imdb_id:
            print(f"❌ No TMDb ID found, trying IMDb ID {imdb_id}")
            tmdb_id = get_tmdb_id_from_imdb(imdb_id)
        poster_path = get_poster_path(tmdb_id, "movie") if tmdb_id else None
        download_poster(poster_path, f"movie{i}.jpg")

    print("\n📺 Updating most recent TV show posters...")
    tv_items = fetch_simkl_data("tv", count=6)
    for i, item in enumerate(tv_items, start=1):
        simkl_id = item.get("id")
        tmdb_id, imdb_id = get_ids_from_simkl("show", simkl_id)
        if not tmdb_id and imdb_id:
            print(f"❌ No TMDb ID found, trying IMDb ID {imdb_id}")
            tmdb_id = get_tmdb_id_from_imdb(imdb_id)
        if tmdb_id:
            poster_path = get_poster_path(tmdb_id, "tv")
            download_poster(poster_path, f"show{i}.jpg")
        else:
            print(f"❌ No TMDb ID for show ID {simkl_id}, skipping...")

if __name__ == "__main__":
    update_posters()
