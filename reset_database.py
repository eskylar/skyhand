import sqlite3
from db_setup import setup_database

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'

# Drop existing tables if they exist
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Tracks')
cur.execute('DROP TABLE IF EXISTS AudioFeatures')
cur.execute('DROP TABLE IF EXISTS Lyrics')

conn.commit()
conn.close()

# Rebuild the tables
setup_database()
print("Database reset and tables recreated.")
