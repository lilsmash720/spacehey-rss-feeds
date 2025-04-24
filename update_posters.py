import os
import requests

# === CONFIG ===
SIMKL_API_KEY = "8c52a7574f3fde132621ec4989da2d688e65198578b09d37bea2607c7bdc253a"
POSTER_DIR = "posters"
BASE_URL = "https://api.simkl.com"  # Simkl base URL

os.makedirs(POSTER_DIR, exist_ok=True)

def fetch_simkl_data(type_, count=6):
    # Construct the correct endpoint URL
    if type_ == "movie":
        url = f"{BASE_URL}/movies/trending"
    else:
        url = f"{BASE_URL}/shows/trending"

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
    
    # Directly use the response as a list
    items = res.json()  # The response is a list now
    
    return items

def download_poster(poster_url, filename):
    if not poster_url:
        print(f"❌ No poster URL for {filename}")
        return

    # Construct the full URL to the poster image
    full_url = f"https://simkl.com/posters/{poster_url}"
    img_data = requests.get(full_url).content

    with open(os.path.join(POSTER_DIR, filename), "wb") as f:
        f.write(img_data)
    print(f"✅ Downloaded {filename} from Simkl.")

def update_posters():
    print("\n🎬 Updating most recent movie posters...")
    movie_items = fetch_simkl_data("movie")
    for i, item in enumerate(movie_items, start=1):
        poster_url = item.get("poster")
        if poster_url:
            download_poster(poster_url, f"movie{i}.jpg")
        else:
            print(f"❌ No poster found for movie {i}.")

    print("\n📺 Updating most recent TV show posters...")
    tv_items = fetch_simkl_data("tv")
    for i, item in enumerate(tv_items, start=1):
        poster_url = item.get("poster")
        if poster_url:
            download_poster(poster_url, f"show{i}.jpg")
        else:
            print(f"❌ No poster found for TV show {i}.")

if __name__ == "__main__":
    update_posters()


