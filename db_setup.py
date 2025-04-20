def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # NEW: Artists table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    # Lyrics table
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

    # Tracks table
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

    conn.commit()
    conn.close()
