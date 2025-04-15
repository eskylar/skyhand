import requests
import sqlite3
import time
import random
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

DB_NAME = '/Users/hannahtoppel/Desktop/si 206/skyhand/music_data.sqlite'
LIMIT_PER_RUN = 25

def setup_database_genius():
    """Ensure the database and tables are created."""
    setup_database()

def search_genius_songs(artist, per_page=5, page=1):
    """Search the Genius API for songs by a given artist with pagination."""
    url = f'{BASE_URL}/search'
    params = {'q': artist, 'per_page': per_page, 'page': page}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Error searching for {artist}: {response.status_code}")
        return []
    return response.json()['response']['hits'][:per_page]

def extract_song_data(hit):
    """Extract song data from a single Genius API hit and return a dictionary."""
    song = hit['result']
    song_data = {
        'song_id': song['id'],
        'title': song['title'],
        'artist': song['primary_artist']['name'],
        'album': song.get('album', {}).get('name', 'Unknown'),
        'release_date': song.get('release_date', 'Unknown'),
        'annotation_count': song.get('annotation_count', 0),
        'has_annotations': 1 if song.get('annotation_count', 0) > 0 else 0,
        'lyrics': ''  # Placeholder since full lyrics are not provided in the search result
    }
    return song_data

def store_lyrics_metadata(song_data):
    """Insert the song data into the Lyrics table."""
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
    Run the Genius data collection process, adding up to LIMIT_PER_RUN new songs.
    This version cycles through the list of artists one by one using a simple index.
    """
    setup_database_genius()  # Ensure that the database/tables exist
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Get current total number of songs in the Lyrics table
    cur.execute("SELECT COUNT(*) FROM Lyrics")
    current_total = cur.fetchone()[0]
    desired_total = 125  # overall target
    if current_total >= desired_total:
        print(f"Database already has {current_total} songs. No need to add more.")
        conn.close()
        return
    
    to_add = LIMIT_PER_RUN  # new songs to add this run
    new_songs = 0

    # Create a dictionary for pagination for each artist
    pages = {artist: 1 for artist in ARTISTS}
    
    # Shuffle the artist list to randomize the order
    artists_shuffled = ARTISTS[:]  # copy of the list
    random.shuffle(artists_shuffled)
    
    # Use a simple index to cycle through artists
    index = 0
    num_artists = len(artists_shuffled)
    
    while to_add > 0:
        current_artist = artists_shuffled[index]
        page = pages[current_artist]
        hits = search_genius_songs(current_artist, per_page=5, page=page)
        if not hits:
            # If no hits on this page, increment the page counter for this artist and move on
            pages[current_artist] += 1
        else:
            for hit in hits:
                if to_add <= 0:
                    break
                song_data = extract_song_data(hit)
                # Check if the song already exists in the Lyrics table
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
            # Increment the page counter for this artist for the next cycle
            pages[current_artist] += 1
        
        # Increment the index. If we've reached the end of the shuffled artist list, start over.
        index = (index + 1) % num_artists

    conn.close()
    print(f"Done. Added {new_songs} Genius songs. Total songs is now {current_total}.")

if __name__ == '__main__':
    run_genius_collection()




