import sqlite3

def setup_database():
    conn = sqlite3.connect('music_data.sqlite')
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
            has_annotations INTEGER
        )
    ''')

    # Tracks table (Spotify API)
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