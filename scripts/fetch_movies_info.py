import os
import requests
import time
import pandas as pd

BASE_URL = 'https://api.themoviedb.org/3'
COUNTRY_CODE = 'US'
TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlYWMxODE3YmE0NWQ0MmQyZDkyZDQ0YjdiZTkzNDg1OCIsIm5iZiI6MTczMTM5NDcyOS42MDIxNTcsInN1YiI6IjY3MzJlNzc2ODU1Y2JiNGU0OGY2NzQyZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.DmOLbEZWZ6fW3Z9jIvcwqKrAdyb6sq-yuetm6bqUm8c'

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_movies_by_year(year):
    """
    Fetch movies released in theaters in the US for a given year.
    
    Parameters:
        year (int): The release year of movies to retrieve.
        
    Returns:
        list of dict: A list of movies with their id and title.
    """
    url = f"{BASE_URL}/discover/movie"
    params = {
        'primary_release_year': year,
        'with_release_type': '3',  # Ensures only full theatrical releases
        'region': COUNTRY_CODE,
        'page': 1,
        'include_adult': False,
        'vote_count.gte': 100
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    all_movies = []

    while True:
        print(f"Requesting page {params['page']} for year {year}...")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error: status code {response.status_code}")
            break
        
        data = response.json()
        
        if 'results' not in data:
            print("No results found in response.")
            break

        print(f"Retrieved {len(data['results'])} movies from page {data['page']} of {data['total_pages']}")  # Debug print
        all_movies.extend(data['results'])
        
        if data['page'] >= data['total_pages']:
            break
        else:
            params['page'] += 1
        
        time.sleep(0.2)  # Delay to avoid hitting TMDB rate limits

    return [{'id': movie['id'], 'title': movie['title']} for movie in all_movies]

# Fetch movies for each year from 2014 to 2024 and save to CSV in data folder
movies = []
for year in range(2014, 2025):
    yearly_movies = get_movies_by_year(year)
    print(f"Retrieved {len(yearly_movies)} movies for {year}")
    print(f"Sample movies for {year}: {[movie['title'] for movie in yearly_movies[:5]]}")
    movies.extend(yearly_movies)

# Convert to a DataFrame for easier handling
movies_df = pd.DataFrame(movies)
print(movies_df.head(5))
movies_csv_path = os.path.join(DATA_DIR, 'theater_released_movies_2014_2024.csv')
movies_df.to_csv(movies_csv_path, index=False)
print(f"Movies data saved to {movies_csv_path}")

def check_streaming_availability(movie_id, country_code=COUNTRY_CODE, major_providers=['Netflix', 'Amazon Prime Video', 'Disney+', 'Hulu', 'HBO Max']):
    """
    Check if a movie is available on specified major streaming platforms in a given country.

    Parameters:
        movie_id (int): The unique ID of the movie to check for streaming availability.
        country_code (str): Code representing the country for which streaming availability should be checked. Defaults to 'US' for this code.
        major_providers (list of str): A list of major streaming platform names to filter results by. Defaults to ['Netflix', 'Amazon Prime Video', 'Disney+', 'Hulu', 'HBO Max'].

    Returns:
        list of str: A list of major streaming providers where the movie is available.  If none of the major providers are available, returns an empty list.
    """
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return []  # When request fail
    
    data = response.json()
    providers = data.get("results", {}).get(country_code, {}).get("flatrate", [])
    provider_names = [provider['provider_name'] for provider in providers]
    print("provider_names for ", movie_id, " is ", provider_names)
    # Filter for only major providers
    major_available_providers = [provider for provider in provider_names if provider in major_providers]
    return major_available_providers

# Check streaming availibility for theater released movies from 2014-2024
movies_df['major_streaming_providers'] = movies_df['id'].apply(check_streaming_availability)
movies_df['is_on_major_streaming'] = movies_df['major_streaming_providers'].apply(lambda x: len(x) > 0)

movies_with_streaming_csv_path = os.path.join(DATA_DIR, 'theater_released_movies_with_streaming_info.csv')
movies_df.to_csv(movies_with_streaming_csv_path, index=False)
print(f"Movies with streaming info saved to {movies_with_streaming_csv_path}")