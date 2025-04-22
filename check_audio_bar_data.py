import sqlite3

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

query = '''
    SELECT L.has_annotations,
           T.name,
           L.title,
           AR.name,
           A.tempo,
           A.energy,
           A.loudness
    FROM Lyrics L
    JOIN Tracks T ON INSTR(LOWER(T.name), LOWER(L.title)) > 0
    JOIN AudioFeatures A ON T.track_id = A.track_id
    JOIN Artists AR ON T.artist_id = AR.id
    WHERE L.artist_id = AR.id
'''

cur.execute(query)
results = cur.fetchall()

print(f"Total matches: {len(results)}")
for row in results[:10]:
    print(row)

conn.close()
