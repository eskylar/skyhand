import requests
import sqlite3
import time
import random
import unicodedata
from db_setup import setup_database

# Genius API Setup
ACCESS_TOKEN = '0Oc4fI4JUTbqzL-wDhf7i4OWKBWB82pa7QQAXqmu2q7jSxImIo3DS5Giyc-u7pkN'
HEADERS = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
BASE_URL = 'https://api.genius.com'

ARTISTS = [
    'Beyonce', 'Caamp', 'Drake', 'Ariana Grande', 'The Weeknd',
    'Rihanna', 'Selena Gomez', 'Queen', 'The Neighbourhood',
    'Lorde', 'Macklemore', 'Journey', 'AC/DC', 'Steve Lacy', 'Brent Faiyaz'
]

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'
LIMIT_PER_RUN = 25

def setup_database_genius():
    """Ensure that the database and tables are set up before collecting Genius data."""
    setup_database()

def normalize_text(text):
    """Normalize text by removing accents, lowercasing, and trimming spaces."""
    nkfd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nkfd_form if not unicodedata.combining(c)]).lower().strip()

def search_genius_songs(artist, per_page=5, page=1):
    """Search Genius API for songs by a given artist with pagination."""
    url = f'{BASE_URL}/search'
    params = {'q': artist, 'per_page': per_page, 'page': page}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Error searching for {artist}: {response.status_code}")
        return []
    return response.json()['response']['hits'][:per_page]

def extract_song_data(hit, searched_artist):
    """
    Extract song data from a Genius API hit.
    Only return song data if the normalized primary artist matches the searched artist.
    """
    song = hit['result']
    primary_artist = song['primary_artist']['name']
    if normalize_text(primary_artist) != normalize_text(searched_artist):
        return None  # Skip if not an exact match
    song_data = {
        'song_id': song['id'],
        'title': song['title'],
        'artist': primary_artist,
        'album': song.get('album', {}).get('name', 'Unknown'),
        'release_date': song.get('release_date', 'Unknown'),
        'annotation_count': song.get('annotation_count', 0),
        'has_annotations': 1 if song.get('annotation_count', 0) > 0 else 0,
        'lyrics': ''  # Placeholder
    }
    return song_data

def store_lyrics_metadata(song_data):
    """Insert the extracted song metadata into the Lyrics table."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT OR IGNORE INTO Lyrics (song_id, title, artist, album, release_date, annotation_count, has_annotations, lyrics)
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
    print(f"Inserted lyrics for {song_data['title']} by {song_data['artist']}")
    conn.commit()
    conn.close()

def run_genius_collection():
    """
    Run the Genius data collection process. This version cycles through a randomized 
    list of artists using a simple index, ensuring that 25 new songs come from various artists.
    It only inserts songs where the primary artist matches the searched artist.
    """
    setup_database_genius()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Lyrics")
    current_total = cur.fetchone()[0]
    desired_total = 125
    if current_total >= desired_total:
        print(f"Database already has {current_total} songs. No need to add more.")
        conn.close()
        return

    to_add = LIMIT_PER_RUN
    new_songs = 0

    # Initialize per-artist page counters
    pages = {artist: 1 for artist in ARTISTS}
    artists_shuffled = ARTISTS[:]  # copy list
    random.shuffle(artists_shuffled)
    index = 0
    num_artists = len(artists_shuffled)

    while to_add > 0:
        current_artist = artists_shuffled[index]
        page = pages[current_artist]
        hits = search_genius_songs(current_artist, per_page=5, page=page)
        if not hits:
            pages[current_artist] += 1
        else:
            for hit in hits:
                if to_add <= 0:
                    break
                song_data = extract_song_data(hit, current_artist)
                if song_data is None:
                    continue
                cur.execute("SELECT 1 FROM Lyrics WHERE song_id = ?", (song_data['song_id'],))
                if cur.fetchone() is None:
                    store_lyrics_metadata(song_data)
                    new_songs += 1
                    to_add -= 1
                    current_total += 1
                    if current_total >= desired_total:
                        print(f"Desired total reached: {current_total} songs in database.")
                        conn.close()
                        return
                time.sleep(0.5)
            pages[current_artist] += 1

        index = (index + 1) % num_artists

    conn.close()
    print(f"Done. Added {new_songs} Genius songs. Total songs is now {current_total}.")

if __name__ == '__main__':
    run_genius_collection()




