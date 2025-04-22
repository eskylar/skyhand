import sqlite3

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# Check total rows in AudioFeatures
cur.execute("SELECT COUNT(*) FROM AudioFeatures")
audio_count = cur.fetchone()[0]
print(f"Total rows in AudioFeatures: {audio_count}")

# Preview some rows
cur.execute('''
    SELECT A.track_id, A.tempo, A.energy, A.loudness, T.name, AR.name
    FROM AudioFeatures A
    JOIN Tracks T ON A.track_id = T.track_id
    JOIN Artists AR ON T.artist_id = AR.id
    LIMIT 10
''')
sample = cur.fetchall()

print("\nSample linked audio features:")
for row in sample:
    print(row)

conn.close()
