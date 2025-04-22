import sqlite3

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables in the database:", tables)

cur.execute("PRAGMA table_info(Artists)")
columns = cur.fetchall()
print("Artists table columns:")
for col in columns:
    print(col)

conn.close()
