import os
import sqlite3

DB_NAME = os.path.join(os.path.dirname(__file__), 'music_data.sqlite')

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Lyrics table (Genius API)
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

    # Create Tracks table
    # Tracks table (Spotify API) with additional duration_ms column
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Tracks (
            track_id TEXT PRIMARY KEY,
            name TEXT,
            artist TEXT,
            album TEXT,
            popularity INTEGER,
            release_date TEXT,
            genres TEXT,
            duration_ms INTEGER
        )
    ''')

    # Create AudioFeatures table
    # AudioFeatures table (Spotify API)
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
