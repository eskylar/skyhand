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

DB_NAME = '/Users/hannahtoppel/Desktop/si 206/skyhand/music_data.sqlite'
LIMIT_PER_RUN = 25

def setup_database_genius():
    """
    Ensure that the database and tables are set up before collecting Genius data.
    """
    setup_database()

def search_genius_songs(artist, per_page=5, page=1):
    """
    Search Genius API for songs by a given artist with pagination.
    
    Args:
        artist (str): The artist name.
        per_page (int): Maximum number of results per page.
        page (int): Page number for the API.
    
    Returns:
        list: A list of hit items from the API.
    """
    url = f'{BASE_URL}/search'
    params = {'q': artist, 'per_page': per_page, 'page': page}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Error searching for {artist}: {response.status_code}")
        return []
    return response.json()['response']['hits'][:per_page]



def extract_song_data(hit):
    """
    Extract song data from a Genius API hit.
    
    Args:
        hit (dict): A single hit result from the API.
    
    Returns:
        dict: A dictionary containing song metadata.
    """
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
    """
    Store the extracted song metadata into the Lyrics table.
    
    Args:
        song_data (dict): The song metadata dictionary.
    """
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
    Run the Genius data collection process, adding up to LIMIT_PER_RUN (25) new songs per run.
    The script checks the current total and adds songs incrementally until a desired total of 125 is reached.
    """
    setup_database_genius()  # Ensure the database/tables exist
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Get current total number of songs in the Lyrics table
    cur.execute("SELECT COUNT(*) FROM Lyrics")
    current_total = cur.fetchone()[0]
    
    desired_total = 125  # overall target number of songs
    if current_total >= desired_total:
        print(f"Database already has {current_total} songs. No need to add more.")
        conn.close()
        return
    
    to_add = LIMIT_PER_RUN  # maximum new songs to add this run (e.g., 25)
    new_songs = 0

    # Loop over each artist and try to fetch new songs using pagination if necessary
    for artist in ARTISTS:
        if to_add <= 0:
            break
        page = 1
        while to_add > 0:
            hits = search_genius_songs(artist, per_page=5, page=page)
            if not hits:  # no more hits for this artist on this page
                break
            for hit in hits:
                if to_add <= 0:
                    break
                song_data = extract_song_data(hit)
                # Check if song already exists
                cur.execute("SELECT 1 FROM Lyrics WHERE song_id = ?", (song_data['song_id'],))
                if cur.fetchone() is None:
                    store_lyrics_metadata(song_data)
                    new_songs += 1
                    to_add -= 1
                    current_total += 1
                    # If we reach our desired total, stop immediately.
                    if current_total >= desired_total:
                        print(f"Desired total reached: {current_total} songs in database.")
                        conn.close()
                        return
                time.sleep(0.5)
            page += 1

    conn.close()
    print(f"Done. Added {new_songs} Genius songs. Total songs is now {current_total}.")



if __name__ == '__main__':
    run_genius_collection()




