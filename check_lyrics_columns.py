import sqlite3

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("PRAGMA table_info(Lyrics)")
columns = cur.fetchall()

print("Lyrics table columns:")
for col in columns:
    print(col)

conn.close()
