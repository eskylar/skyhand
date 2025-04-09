import sqlite3

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'

def setup_database():
    """
    Set up the SQLite database with the necessary tables:
      - Lyrics: stores Genius metadata including lyrics.
      - Tracks: stores Spotify track data including a genres column.
      - AudioFeatures: stores audio features for each track.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Create Lyrics table (Genius API) with a lyrics column
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Lyrics (
            song_id INTEGER PRIMARY KEY,
            title TEXT,
            artist TEXT,
            album TEXT,
            release_date TEXT,
            annotation_count INTEGER,
            has_annotations INTEGER,
            lyrics TEXT
        )
    ''')

    # Create Tracks table (Spotify API) with a genres column
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

    # Create AudioFeatures table (Spotify API)
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

if __name__ == '__main__':
    setup_database()
