import requests
import sqlite3
import time

# ---------------------------------------------
# Spotify API Setup (Use your own access token)
# ---------------------------------------------
ACCESS_TOKEN = 'BQBqs6Os7mGPkoOWzWqoEgDnMX1KO575pPMMcrlwRuvzi4ayI69w7sH0eCktNGDREKUySUVtjjiD72OlMfBR6HvOoLCtDRLMgQHPEOrhmmkFoFH5rp7L6WgmC-KUvVP8haHYp1V-vlQ'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}
BASE_URL = 'https://api.spotify.com/v1'

ARTISTS = [
    'Beyonce', 'Caamp', 'Drake', 'Ariana Grande', 'The Weeknd',
    'Rihanna', 'Selena Gomez', 'Queen', 'The Neighbourhood',
    'Lorde', 'Macklemore', 'Journey', 'AC/DC', 'Steve Lacy', 'Brent Faiyaz'
]

# UPDATED DB path here:
DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'
LIMIT_PER_RUN = 25  # Reduced limit per run

def setup_database():
    """
    Set up the SQLite database tables for Tracks and AudioFeatures,
    including the genres column in Tracks.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Create Tracks table with genres column
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Tracks (
            track_id TEXT PRIMARY KEY,
            name TEXT,
            artist TEXT,
            album TEXT,
            popularity INTEGER,
            release_date TEXT,
            genres TEXT
        )
    ''')

    # Create AudioFeatures table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS AudioFeatures (
            track_id TEXT PRIMARY KEY,
            tempo REAL,
            energy REAL,
            key INTEGER,
            loudness REAL,
            FOREIGN KEY(track_id) REFERENCES Tracks(track_id)
        )
    ''')

    conn.commit()
    conn.close()


def search_tracks_by_artist(artist_name, limit=15, offset=0):
    """
    Search for tracks by a given artist using the Spotify API.
    
    Args:
        artist_name (str): The artist name.
        limit (int): Number of tracks to return.
        offset (int): Offset value for pagination.
    
    Returns:
        list: A list of track items.
    """
    params = {
        'q': artist_name,
        'type': 'track',
        'limit': limit,
        'offset': offset
    }
    response = requests.get(BASE_URL + '/search', headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Error fetching tracks for {artist_name}: {response.status_code}")
        print(f"Error message: {response.text}")
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
    """
    Store track metadata and its audio features into the database.
    
    Args:
        track (dict): The track data from Spotify.
        conn (Connection): The SQLite connection object.
        cur (Cursor): The SQLite cursor object.
    """
    try:
        artist_info = track['artists'][0]
        artist_id = artist_info['id']
        genres_list = get_artist_genres(artist_id)
        genres_str = ", ".join(genres_list) if genres_list else "Unknown"

        # Print a concise message indicating the song added
        print(f"Added: {track['name']} by {artist_info['name']}")

        cur.execute('''
            INSERT OR REPLACE INTO Tracks (track_id, name, artist, album, popularity, release_date, genres)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            track['id'],
            track['name'],
            artist_info['name'],
            track['album']['name'],
            track['popularity'],
            track['album']['release_date'],
            genres_str
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
    """
    Run the Spotify data collection process, adding up to 25 new tracks per run.
    """
    setup_database()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Tracks")
    total_tracks_before = cur.fetchone()[0]
    print(f"Tracks in database before adding new ones: {total_tracks_before}")
    to_add = LIMIT_PER_RUN

    for artist in ARTISTS:
        if to_add <= 0:
            break
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



