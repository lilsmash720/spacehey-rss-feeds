import feedparser
import re
import os
import requests
import tmdbv3api  # Make sure to install tmdbv3api: pip install tmdbv3api

# TMDb API Key
tmdb_api_key = '08d2466ce60a24dce25b03cc1ae3f497'
tmdb = tmdbv3api.TMDb()
tmdb.api_key = tmdb_api_key
movie_search = tmdbv3api.Movie()

# RSS feed URLs
feeds = {
    "movies": "https://api.simkl.com/feeds/list/movies/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us",
    "tv": "https://api.simkl.com/feeds/list/tv/completed/rss/?token=8aa77c51a4eeb0f2762a07937af73f46&client_id=feeds&country=us"
}

# Directory to save images
image_dir = "images"

# Ensure the image directory exists
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# Function to extract movie title from the RSS entry
def extract_movie_title(entry):
    # The title is usually in the 'title' field of the RSS entry
    return entry.title if 'title' in entry else None

# Function to get the poster from TMDb
def get_poster_from_tmdb(movie_title):
    search_results = movie_search.search(movie_title)
    if search_results:
        movie = search_results[0]  # Get the first result (most relevant)
        if movie.poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{movie.poster_path}"  # 500px wide image
            return poster_url
    return None

# Function to download the image and save with a static filename
def download_image(img_url, image_filename):
    try:
        response = requests.get(img_url)
        if response.status_code == 200:
            with open(os.path.join(image_dir, image_filename), 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {image_filename}")
        else:
            print(f"Failed to download {img_url}")
    except Exception as e:
        print(f"Error downloading {img_url}: {e}")

# Iterate over the feeds and download images
for name, url in feeds.items():
    d = feedparser.parse(url)
    for index, entry in enumerate(d.entries[:6]):  # Limit to 6 images
        movie_title = extract_movie_title(entry)
        if movie_title:
            print(f"Searching for {movie_title} on TMDb...")
            poster_url = get_poster_from_tmdb(movie_title)
            if poster_url:
                img_filename = f"movie{index+1}.jpg"  # Static filenames like movie1.jpg, movie2.jpg, etc.
                download_image(poster_url, img_filename)  # Save the image with a static filename

