import requests
import sqlite3
import time
import random
from db_setup import setup_database

#insert or ignore into so no double songs

# Spotify API Setup with your current access token
ACCESS_TOKEN = 'BQBHwRgRP_d8T0duE6M3MmhYqfzQrVtmZoe5yp198sB5-pi5_2AAjlp25grYXMMFdI8gzU3bMwTtm_LKbDnD2eGKW6hFAppMl3FcAu8d2euGD8ZUQE-FpjX8v3n5NU3OMc3ptig_mm8'
HEADERS = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
BASE_URL = 'https://api.spotify.com/v1'

ARTISTS = [
   'Beyonce', 'Caamp', 'Drake', 'Ariana Grande', 'The Weeknd',
   'Rihanna', 'Selena Gomez', 'Queen', 'The Neighbourhood',
   'Lorde', 'Macklemore', 'Journey', 'AC/DC', 'Steve Lacy', 'Brent Faiyaz'
]

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'
LIMIT_PER_RUN = 25 

def setup_database_spotify():
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

def get_artist_genres(artist_id):
    url = f"{BASE_URL}/artists/{artist_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching artist genres for {artist_id}: {response.status_code}")
        return []
    data = response.json()
    return data.get('genres', [])

def store_track(track, conn, cur):
    try:
        artist_info = track['artists'][0]
        artist_id = artist_info['id']
        genres_list = get_artist_genres(artist_id)
        genres_str = ", ".join(genres_list) if genres_list else "Unknown"
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
    except Exception as e:
        print(f"Error storing data for {track['name']} by {artist_info['name']}: {e}")

def run_spotify_collection():
    setup_database_spotify()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Tracks")
    total_before = cur.fetchone()[0]
    print(f"Tracks in database before adding new ones: {total_before}")
    to_add = LIMIT_PER_RUN

    for artist in ARTISTS:
        if to_add <= 0:
            break
        offset = 0  # Using the first page for mainstream results
        tracks = search_tracks_by_artist(artist, limit=15, offset=offset)
        for track in tracks:
            cur.execute("SELECT 1 FROM Tracks WHERE track_id = ?", (track['id'],))
            if cur.fetchone() is None:
                store_track(track, conn, cur)
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
