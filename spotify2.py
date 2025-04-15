import os
import requests
import sqlite3
import time

# ---------------------------------------------
# Spotify API Setup (Use your own access token)
# ---------------------------------------------
ACCESS_TOKEN = 'BQBng9gnUwPhi5YpfssM-AhTKZyvDjHdFNGG05f5R-Qvfb7Vo4I1m4BSvVbv1dTgBLcSd6c6uBCqP7aMsHxq5SLeE6jSyi7_Ld8Y2u2JLyl9906jGuaDX1vg-XRC_6CqQlS5hn_YDAw'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}
BASE_URL = 'https://api.spotify.com/v1'

# Artists to search
ARTISTS = [
    'Beyonce', 'Caamp', 'Drake', 'Ariana Grande', 'The Weeknd',
    'Rihanna', 'Selena Gomez', 'Queen', 'The Neighbourhood',
    'Lorde', 'Macklemore', 'Journey', 'AC/DC', 'Steve Lacy', 'Brent Faiyaz'
]

# Cross-platform DB path
DB_NAME = os.path.join(os.path.dirname(__file__), 'music_data.sqlite')
LIMIT_PER_RUN = 25  # Limit to 25 new songs per run

def setup_database():
    """Set up SQLite database tables for Tracks and AudioFeatures."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Tracks table
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

    # Audio features table
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
    """Search for tracks by artist using Spotify API."""
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
    return response.json().get('tracks', {}).get('items', [])

def get_audio_features(track_id):
    """Get audio features for a track by ID."""
    url = f"{BASE_URL}/audio-features/{track_id}"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else None

def get_artist_genres(artist_id):
    """Get genres for an artist."""
    url = f"{BASE_URL}/artists/{artist_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching genres for artist {artist_id}: {response.status_code}")
        return []
    return response.json().get('genres', [])

def store_track_and_features(track, conn, cur):
    """Store track metadata and audio features in the database."""
    try:
        artist_info = track['artists'][0]
        artist_id = artist_info['id']
        genres_list = get_artist_genres(artist_id)
        genres_str = ", ".join(genres_list) if genres_list else "Unknown"

        print(f"Added: {track['name']} by {artist_info['name']}")

        # Insert into Tracks
        cur.execute('''
            INSERT OR REPLACE INTO Tracks 
            (track_id, name, artist, album, popularity, release_date, genres)
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

        # Insert into AudioFeatures
        features = get_audio_features(track['id'])
        if features:
            cur.execute('''
                INSERT OR REPLACE INTO AudioFeatures 
                (track_id, tempo, energy, key, loudness)
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
        print(f"Error storing track: {e}")

def run_spotify_collection():
    """Main function to run Spotify data collection."""
    setup_database()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Tracks")
    total_before = cur.fetchone()[0]
    print(f"Tracks before: {total_before}")
    to_add = LIMIT_PER_RUN

    for artist in ARTISTS:
        if to_add <= 0:
            break
        tracks = search_tracks_by_artist(artist)
        for track in tracks:
            cur.execute("SELECT 1 FROM Tracks WHERE track_id = ?", (track['id'],))
            if cur.fetchone() is None:
                store_track_and_features(track, conn, cur)
                to_add -= 1
                if to_add <= 0:
                    break
                time.sleep(0.5)

    conn.close()

    # Print updated total
    conn_check = sqlite3.connect(DB_NAME)
    cur_check = conn_check.cursor()
    cur_check.execute("SELECT COUNT(*) FROM Tracks")
    total_now = cur_check.fetchone()[0]
    conn_check.close()

    print(f"Done. {LIMIT_PER_RUN - to_add} new tracks added. Total now: {total_now}")

if __name__ == '__main__':
    run_spotify_collection()


