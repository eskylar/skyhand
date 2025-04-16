import sqlite3

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'

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

    # Tracks table (Spotify API) – note: duration_ms is stored as an INTEGER
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
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
