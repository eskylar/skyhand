import sqlite3

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Tracks (
            track_id TEXT PRIMARY KEY,
            name TEXT,
            artist_id INTEGER,
            album TEXT,
            popularity INTEGER,
            release_date TEXT,
            genres TEXT,
            duration_ms INTEGER,
            FOREIGN KEY (artist_id) REFERENCES Artists(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Lyrics (
            song_id INTEGER PRIMARY KEY,
            title TEXT,
            artist_id INTEGER,
            album TEXT,
            release_date TEXT,
            annotation_count INTEGER,
            has_annotations INTEGER,
            lyrics TEXT,
            FOREIGN KEY (artist_id) REFERENCES Artists(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS AudioFeatures (
            track_id TEXT PRIMARY KEY,
            tempo REAL,
            energy REAL,
            loudness REAL
        )
    ''')

    conn.commit()
    conn.close()
