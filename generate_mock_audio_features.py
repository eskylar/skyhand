import sqlite3
import random

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'

def generate_mock_audio_features():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Get all track_ids that do NOT already have audio features
    cur.execute('''
        SELECT track_id FROM Tracks
        WHERE track_id NOT IN (SELECT track_id FROM AudioFeatures)
    ''')
    track_ids = [row[0] for row in cur.fetchall()]
    print(f"Generating features for {len(track_ids)} tracks...")

    for track_id in track_ids:
        # Generate realistic ranges for audio features
        tempo = round(random.uniform(60, 180), 2)         # Typical tempo (bpm)
        energy = round(random.uniform(0.3, 0.9), 3)        # Energy between 0–1
        loudness = round(random.uniform(-12, -3), 2)       # Loudness in dB

        cur.execute('''
            INSERT OR IGNORE INTO AudioFeatures (track_id, tempo, energy, loudness)
            VALUES (?, ?, ?, ?)
        ''', (track_id, tempo, energy, loudness))

    conn.commit()
    conn.close()
    print("Mock audio features inserted successfully.")

if __name__ == '__main__':
    generate_mock_audio_features()
