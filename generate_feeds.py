import feedparser
import re
import os
import requests

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

# Function to extract image URL from the summary
def extract_image_url(entry):
    # Check if 'summary' exists in entry and extract image URL if it does
    if 'summary' in entry:
        match = re.search(r'<img src="(.*?)"', entry.summary)
        return match.group(1) if match else None
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
        img_url = extract_image_url(entry)
        if img_url:
            img_filename = f"movie{index+1}.jpg"  # Static filenames like movie1.jpg, movie2.jpg, etc.
            download_image(img_url, img_filename)  # Save the image with a static filename

