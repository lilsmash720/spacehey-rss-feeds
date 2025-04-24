import requests
import os

# Your Simkl API access details
simkl_api_url = "https://api.simkl.com/v1/"
simkl_api_key = "YOUR_SIMKL_API_KEY"

# Make the request for movies and TV shows
def fetch_simkl_data():
    headers = {'Authorization': f'Bearer {simkl_api_key}'}
    
    # Fetch the first 6 movies
    movie_url = f"{simkl_api_url}movies?limit=6"
    tv_url = f"{simkl_api_url}shows?limit=6"
    
    movies_response = requests.get(movie_url, headers=headers).json()
    shows_response = requests.get(tv_url, headers=headers).json()
    
    return movies_response, shows_response

# Download the posters
def download_posters(movies, shows):
    if not os.path.exists("posters"):
        os.mkdir("posters")
    
    # Process movies
    for i, movie in enumerate(movies):
        poster_path = movie.get('poster')
        if poster_path:
            full_url = f"https://simkl.com/static/media/posters/{poster_path}.jpg"
            download_image(full_url, f"posters/movie{i+1}.jpg")
    
    # Process shows
    for i, show in enumerate(shows):
        poster_path = show.get('poster')
        if poster_path:
            full_url = f"https://simkl.com/static/media/posters/{poster_path}.jpg"
            download_image(full_url, f"posters/show{i+1}.jpg")

# Download the image to local storage
def download_image(url, file_name):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {file_name}: {e}")

# Main function to handle the process
def main():
    movies, shows = fetch_simkl_data()
    download_posters(movies, shows)

if __name__ == "__main__":
    main()
