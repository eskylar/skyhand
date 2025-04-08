import requests
import sqlite3
import time
import json
import random

# ---------------------------------------------
# Spotify API Setup (Use your own access token)
# ---------------------------------------------
ACCESS_TOKEN = 'BQDP2huTaK6SJ02IgPbZOmy8EWlMtU2zx4fYpAbyPwQRAeBnutQmoOQn6iExb_CdeIANqJi0z_mAk0fk3wkszzPQ0cmFym2zRm9cvpROlfi50prbZUk_Ps0CykYS7tF0nP7Pg2MzmXE'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}
BASE_URL = 'https://api.spotify.com/v1'

ARTISTS = [
    'Beyonce', 'Caamp', 'Drake', 'Ariana Grande', 'The Weeknd',
    'Rihanna', 'Selena Gomez', 'Queen', 'The Neighbourhood',
    'Lorde', 'Macklemore', 'Journey', 'AC/DC', 'Steve Lacy', 'Brent Faiyaz'
]

DB_NAME = '/Users/skylaremerson/Desktop/SI206/Final Project/music_data.sqlite'
LIMIT_PER_RUN = 50

# ---------------------------------------------
# Database setup
# ---------------------------------------------
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Create Tracks table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Tracks (
            track_id TEXT PRIMARY KEY,
            name TEXT,
            artist TEXT,
            album TEXT,
            popularity INTEGER,
            release_date TEXT
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

# ---------------------------------------------
# Search tracks by artist name
# ---------------------------------------------
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

# ---------------------------------------------
# Get audio features for a track
# ---------------------------------------------
def get_audio_features(track_id):
    url = f"{BASE_URL}/audio-features/{track_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return None  # Don't print 403s
    return response.json()

# ---------------------------------------------
# Store track and audio features into the database
# ---------------------------------------------
def store_track_and_features(track, conn, cur):
    if not track['preview_url']:
        return  # Skip tracks that aren't playable (to avoid 403 errors)

    try:
        # Debugging: Print the track data being inserted
        print(f"Inserting track: {track['name']} by {track['artists'][0]['name']}")

        # Insert into Tracks
        cur.execute('''
            INSERT OR REPLACE INTO Tracks (track_id, name, artist, album, popularity, release_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            track['id'],
            track['name'],
            track['artists'][0]['name'],
            track['album']['name'],
            track['popularity'],
            track['album']['release_date']
        ))

        # Debugging: Check if insertion of track was successful
        conn.commit()
        print(f"Track {track['name']} inserted successfully into Tracks table.")

        # Get audio features and insert
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

            # Debugging: Commit after audio feature insertion
            conn.commit()
            print(f"Audio features for {track['name']} inserted successfully into AudioFeatures table.")

        # Check the number of tracks in the database after commit
        cur.execute("SELECT COUNT(*) FROM Tracks")
        print(f"Tracks in database after insertion: {cur.fetchone()[0]}")

    except Exception as e:
        print(f"Error storing data for {track['name']} by {track['artists'][0]['name']}: {e}")



# ---------------------------------------------
# Run the data collection (limit to 50 tracks per run)
# ---------------------------------------------
def run_spotify_collection():
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
        offset = random.randint(0, 40)
        tracks = search_tracks_by_artist(artist, limit=15, offset=offset)
        for track in tracks:
            cur.execute("SELECT 1 FROM Tracks WHERE track_id = ?", (track['id'],))
            if cur.fetchone() is None:
                store_track_and_features(track, conn, cur)  # Pass both conn and cur here
                to_add -= 1
                if to_add <= 0:
                    break
                time.sleep(0.5)

    conn.close()

    # Open a new connection to count total tracks after adding
    conn_check = sqlite3.connect(DB_NAME)
    cur_check = conn_check.cursor()
    cur_check.execute("SELECT COUNT(*) FROM Tracks")
    total_now = cur_check.fetchone()[0]
    conn_check.close()

    print(f"Done. {(LIMIT_PER_RUN - to_add)} new tracks added (if available). Total now: {total_now}")

# ---------------------------------------------
# Run script
# ---------------------------------------------
if __name__ == '__main__':
    run_spotify_collection()
