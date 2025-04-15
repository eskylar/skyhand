import os
import requests
import sqlite3
import time
from db_setup import setup_database

# ---------------------------------------------
# Genius API Setup (Use your own access token)
# ---------------------------------------------
ACCESS_TOKEN = 'jnucUJZcF2kUdD3871ul6Rgtpzd6H0CGbfhnULICOeHxJ4Nn1FCwq-9vhp3OCCqT'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}
BASE_URL = 'https://api.genius.com'

ARTISTS = [
    'Beyonce', 'Caamp', 'Drake', 'Ariana Grande', 'The Weeknd',
    'Rihanna', 'Selena Gomez', 'Queen', 'The Neighbourhood',
    'Lorde', 'Macklemore', 'Journey', 'AC/DC', 'Steve Lacy', 'Brent Faiyaz'
]

#  Automatically get the correct path to the DB file
DB_NAME = os.path.join(os.path.dirname(__file__), 'music_data.sqlite')
LIMIT_PER_RUN = 25

def setup_database_genius():
    """
    Ensure that the database and tables are set up before collecting Genius data.
    """
    setup_database()

def search_genius_songs(artist, per_page=5, page=1):
    """
    Search Genius API for songs by a given artist with pagination.
    """
    print(f" Searching Genius for '{artist}' (page {page})...")
    url = f'{BASE_URL}/search'
    params = {'q': artist, 'per_page': per_page, 'page': page}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f" Error searching for {artist}: {response.status_code}")
            return []
        return response.json()['response']['hits'][:per_page]
    except Exception as e:
        print(f" Failed to fetch data for {artist}: {e}")
        return []

def extract_song_data(hit):
    """
    Extract song data from a Genius API hit.
    """
    song = hit['result']
    return {
        'song_id': song['id'],
        'title': song['title'],
        'artist': song['primary_artist']['name'],
        'album': song.get('album', {}).get('name', 'Unknown'),
        'release_date': song.get('release_date', 'Unknown'),
        'annotation_count': song.get('annotation_count', 0),
        'has_annotations': 1 if song.get('annotation_count', 0) > 0 else 0,
        'lyrics': ''  # Placeholder for now
    }

def store_lyrics_metadata(song_data):
    """
    Store the extracted song metadata into the Lyrics table.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            INSERT OR IGNORE INTO Lyrics 
            (song_id, title, artist, album, release_date, annotation_count, has_annotations, lyrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            song_data['song_id'],
            song_data['title'],
            song_data['artist'],
            song_data['album'],
            song_data['release_date'],
            song_data['annotation_count'],
            song_data['has_annotations'],
            song_data['lyrics']
        ))
        conn.commit()
        conn.close()
        print(f" Inserted: {song_data['title']} by {song_data['artist']}")
    except Exception as e:
        print(f" Error storing song {song_data['title']}: {e}")

def run_genius_collection():
    """
    Add up to LIMIT_PER_RUN (25) new songs per run until reaching 125 songs total.
    """
    setup_database_genius()  # Ensure tables are ready
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Check current number of songs
    cur.execute("SELECT COUNT(*) FROM Lyrics")
    current_total = cur.fetchone()[0]
    conn.close()

    desired_total = 125
    if current_total >= desired_total:
        print(f" Already have {current_total} songs — no need to add more.")
        return

    to_add = LIMIT_PER_RUN
    new_songs = 0

    for artist in ARTISTS:
        if to_add <= 0:
            break
        page = 1
        while to_add > 0:
            hits = search_genius_songs(artist, per_page=5, page=page)
            if not hits:
                break
            for hit in hits:
                if to_add <= 0:
                    break
                song_data = extract_song_data(hit)
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM Lyrics WHERE song_id = ?", (song_data['song_id'],))
                exists = cur.fetchone()
                conn.close()
                if not exists:
                    store_lyrics_metadata(song_data)
                    new_songs += 1
                    to_add -= 1
                    current_total += 1
                    if current_total >= desired_total:
                        print(f" Goal reached: {current_total} total songs.")
                        return
                    time.sleep(0.5)
            page += 1

    print(f" Done. Added {new_songs} songs. Total now: {current_total}")

if __name__ == '__main__':
    run_genius_collection()
