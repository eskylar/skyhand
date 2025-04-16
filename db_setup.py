import sqlite3

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Updated Lyrics table (Genius API) with a lyrics column and song_id as INTEGER PRIMARY KEY
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

    # New Annotations table for additional Genius data, sharing the integer song_id as a foreign key
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Annotations (
            annotation_id INTEGER PRIMARY KEY,
            song_id INTEGER,
            annotation_text TEXT,
            FOREIGN KEY(song_id) REFERENCES Lyrics(song_id)
        )
    ''')
    
    # Updated Tracks table (Spotify API) with "genres" and "duration_ms" columns
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

    # AudioFeatures table remains unchanged (tracks are linked via track_id as TEXT)
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
