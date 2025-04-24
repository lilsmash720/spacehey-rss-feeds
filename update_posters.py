import os
import requests

# === CONFIG ===
SIMKL_API_KEY = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
TMDB_API_KEY = "08d2466ce60a24dce25b03cc1ae3f497"

MOVIES_API_URL = "https://api.simkl.com/movies/trending"
TV_API_URL = "https://api.simkl.com/shows/trending"
POSTER_DIR = "posters"

os.makedirs(POSTER_DIR, exist_ok=True)

# Function to fetch data from Simkl API for movies or TV shows
def fetch_simkl_data(type_, count=6):
    url = MOVIES_API_URL if type_ == "movie" else TV_API_URL
    params = {
        "token": SIMKL_API_KEY,
        "limit": count,
        "country": "us"
    }
    
    res = requests.get(url, params=params)
    
    if res.status_code != 200:
        print(f"❌ Error fetching {type_} data: {res.status_code}")
        return []

    # Debugging: Print the raw response
    print("Raw API Response:", res.json())
    
    data = res.json()  # Assuming the response should be a dictionary
    items = data.get('data', [])  # Assuming the 'data' key contains the list of movies/shows
    
    return items


# Function to fetch the TMDb ID from Simkl API response
def get_tmdb_id_from_simkl(item):
    tmdb_id = item.get('ids', {}).get('tmdb')
    if not tmdb_id:
        print(f"❌ No TMDb ID found for {item['title']}")
        return None
    print(f"🎯 {item['title']} ➡️ TMDb ID: {tmdb_id}")
    return tmdb_id

# Function to fetch the poster path from TMDb
def get_poster_path(tmdb_id, type_):
    print(f"🎬 Fetching poster from TMDb for {type_} ID {tmdb_id}")
    url = f"https://api.themoviedb.org/3/{type_}/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,  # Use the API key as a query parameter
        "language": "en-US"
    }
    res = requests.get(url, params=params)  # Pass params directly to the request
    if res.status_code != 200:
        print(f"❌ TMDb error for {type_} ID {tmdb_id}: {res.status_code}")
        return None
    poster_path = res.json().get("poster_path")
    print(f"🖼️ Poster path for {type_} ID {tmdb_id}: {poster_path}")
    return poster_path

# Function to download the poster
def download_poster(poster_path, filename):
    if not poster_path:
        print(f"❌ No poster path for {filename}")
        return
    url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    img_data = requests.get(url).content
    with open(os.path.join(POSTER_DIR, filename), "wb") as f:
        f.write(img_data)
    print(f"✅ Downloaded {filename}")

# Main function to update the posters for the latest movies and TV shows
def update_posters():
    print("\n🎬 Updating most recent movie posters...")
    movie_items = fetch_simkl_data("movie")
    for i, item in enumerate(movie_items, start=1):
        tmdb_id = get_tmdb_id_from_simkl(item)
        if tmdb_id:
            poster_path = get_poster_path(tmdb_id, "movie")
            download_poster(poster_path, f"movie{i}.jpg")

    print("\n📺 Updating most recent TV show posters...")
    tv_items = fetch_simkl_data("tv")
    for i, item in enumerate(tv_items, start=1):
        tmdb_id = get_tmdb_id_from_simkl(item)
        if tmdb_id:
            poster_path = get_poster_path(tmdb_id, "tv")
            download_poster(poster_path, f"show{i}.jpg")

if __name__ == "__main__":
    update_posters()
