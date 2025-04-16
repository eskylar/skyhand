


import requests
import sqlite3
import time

# ---------------------------------------------
# Spotify API Setup (Use your own access token)
# ---------------------------------------------
ACCESS_TOKEN = 'BQBW2vkq8Z6jMeghvEUSZLuNojCda5_hys4t_0Uy5fI-j0Vx4pJKVbYQaoeFIRFNWDRQmYLbxdeOWbPKIZ7oQVz54MS7q1XPgwuQyu1mn0R9l19p1KW8M5zvq6I6gCe1xG8u6cCV6l4'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}
BASE_URL = 'https://api.spotify.com/v1'

ARTISTS = [
    'Beyonce', 'Caamp', 'Drake', 'Ariana Grande', 'The Weeknd',
    'Rihanna', 'Selena Gomez', 'Queen', 'The Neighbourhood',
    'Lorde', 'Macklemore', 'Journey', 'AC/DC', 'Steve Lacy', 'Brent Faiyaz'
]

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'
LIMIT_PER_RUN = 25  # Limit new tracks per run

def setup_database_spotify():
    """Ensure the Tracks and AudioFeatures tables exist."""
    setup_database()

def search_tracks_by_artist(artist_name, limit=15, offset=0):
    params = {
        'q': artist_name,
        'type': 'track',
        'limit': limit,
        'offset': offset
    }
    response = requests.get(BASE_URL + '/search', headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Error fetching tracks for {artist_name}: {response.status_code}")
        return []
    data = response.json()
    return data['tracks']['items']

def get_audio_features(track_id):
   """
   Retrieve audio features for a track.
  
   Args:
       track_id (str): The Spotify track ID.
  
   Returns:
       dict or None: A dictionary of audio features or None if not found.
   """
   url = f"{BASE_URL}/audio-features/{track_id}"
   response = requests.get(url, headers=HEADERS)
   if response.status_code != 200:
       return None
   return response.json()



def get_artist_genres(artist_id):
    url = f"{BASE_URL}/artists/{artist_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching artist genres for {artist_id}: {response.status_code}")
        return []
    data = response.json()
    return data.get('genres', [])

def store_track_and_features(track, conn, cur):
    try:
        artist_info = track['artists'][0]
        artist_id = artist_info['id']
        genres_list = get_artist_genres(artist_id)
        genres_str = ", ".join(genres_list) if genres_list else "Unknown"

        # Insert track including duration_ms
        print(f"Added: {track['name']} by {artist_info['name']}")
        cur.execute('''
            INSERT OR REPLACE INTO Tracks (
                track_id, name, artist, album, popularity, release_date, genres, duration_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            track['id'],
            track['name'],
            artist_info['name'],
            track['album']['name'],
            track['popularity'],
            track['album']['release_date'],
            genres_str,
            track['duration_ms']
        ))
        conn.commit()

        features = get_audio_features(track['id'])
        if features:
            cur.execute('''
                INSERT OR REPLACE INTO AudioFeatures (track_id, tempo, energy, key, loudness)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                features['id'],
                features['tempo'],
                features['energy'],
                features['key'],
                features['loudness']
            ))
            conn.commit()

    except Exception as e:
        print(f"Error storing data for {track['name']} by {artist_info['name']}: {e}")

def run_spotify_collection():
    setup_database_spotify()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Tracks")
    total_tracks_before = cur.fetchone()[0]
    print(f"Tracks in database before adding new ones: {total_tracks_before}")
    to_add = LIMIT_PER_RUN

    for artist in ARTISTS:
        if to_add <= 0:
            break
        # Always use offset 0 for mainstream tracks
        offset = 0  
        tracks = search_tracks_by_artist(artist, limit=15, offset=offset)
        for track in tracks:
            cur.execute("SELECT 1 FROM Tracks WHERE track_id = ?", (track['id'],))
            if cur.fetchone() is None:
                store_track_and_features(track, conn, cur)
                to_add -= 1
                if to_add <= 0:
                    break
                time.sleep(0.5)
    conn.close()

    conn_check = sqlite3.connect(DB_NAME)
    cur_check = conn_check.cursor()
    cur_check.execute("SELECT COUNT(*) FROM Tracks")
    total_now = cur_check.fetchone()[0]
    conn_check.close()
    print(f"Done. {LIMIT_PER_RUN - to_add} new tracks added (if available). Total now: {total_now}")

if __name__ == '__main__':
    run_spotify_collection()

