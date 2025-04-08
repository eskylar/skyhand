import requests
import sqlite3
import time

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

DB_NAME = '/Users/skylaremerson/Desktop/SI206/Final Project/music_data.sqlite'

LIMIT_PER_RUN = 25

# ---------------------------------------------
# Database setup for both Lyrics and Tracks tables
# ---------------------------------------------
# ---------------------------------------------
# Database setup (modified to include AudioFeatures table)
# ---------------------------------------------
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Create Lyrics table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Lyrics (
            song_id INTEGER PRIMARY KEY,
            title TEXT,
            artist TEXT,
            album TEXT,
            release_date TEXT,
            annotation_count INTEGER,
            has_annotations INTEGER
        )
    ''')

    # Create AudioFeatures table (added this part)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS AudioFeatures (
            track_id TEXT PRIMARY KEY,
            tempo REAL,
            energy REAL,
            key INTEGER,
            loudness REAL
        )
    ''')

    conn.commit()
    conn.close()


# ---------------------------------------------
# Search Genius for songs by artist
# ---------------------------------------------
def search_genius_songs(artist, per_page=5):
    url = f'{BASE_URL}/search'
    params = {'q': artist}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Error searching for {artist}: {response.status_code}")
        return []
    return response.json()['response']['hits'][:per_page]

# ---------------------------------------------
# Simulate metadata and annotations (simplified version)
# ---------------------------------------------
def extract_song_data(hit):
    song = hit['result']
    song_data = {
        'song_id': song['id'],
        'title': song['title'],
        'artist': song['primary_artist']['name'],
        'album': song.get('album', {}).get('name', 'Unknown'),
        'release_date': song.get('release_date', 'Unknown'),
        'annotation_count': song.get('annotation_count', 0),
        'has_annotations': 1 if song.get('annotation_count', 0) > 0 else 0
    }
    return song_data

# ---------------------------------------------
# Store lyrics/metadata into database
# ---------------------------------------------
def store_lyrics_metadata(song_data):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Insert song data into Lyrics table
    cur.execute('''
        INSERT OR IGNORE INTO Lyrics (title, artist, lyrics, has_annotations, annotation_count)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        song_data['title'],
        song_data['artist'],
        song_data['lyrics'],
        song_data['has_annotations'],
        song_data['annotation_count']
    ))

    print(f"Inserted lyrics for {song_data['title']} by {song_data['artist']}")  # Added print statement

    conn.commit()
    conn.close()


# ---------------------------------------------
# Run Genius data collection
# ---------------------------------------------
def run_genius_collection():
    setup_database()  # Make sure the tables are set up before starting
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Lyrics")
    existing = cur.fetchone()[0]
    to_add = LIMIT_PER_RUN

    for artist in ARTISTS:
        if to_add <= 0:
            break
        hits = search_genius_songs(artist)
        for hit in hits:
            song_data = extract_song_data(hit)
            cur.execute("SELECT 1 FROM Lyrics WHERE song_id = ?", (song_data['song_id'],))
            if cur.fetchone() is None:
                store_lyrics_metadata(song_data)
                to_add -= 1
                if to_add <= 0:
                    break
                time.sleep(0.5)

    conn.close()
    print(f"Done. Added {LIMIT_PER_RUN - to_add} Genius songs.")

# ---------------------------------------------
# Run script
# ---------------------------------------------
if __name__ == '__main__':
    run_genius_collection()
