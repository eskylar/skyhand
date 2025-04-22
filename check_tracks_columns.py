import sqlite3

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("PRAGMA table_info(Tracks)")
columns = cur.fetchall()

print("Tracks table columns:")
for col in columns:
    print(col)

conn.close()
