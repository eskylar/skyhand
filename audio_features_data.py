import sqlite3
import requests
import time
from get_spotify_token import get_spotify_token

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'
ACCESS_TOKEN = get_spotify_token()
HEADERS = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
BASE_URL = 'https://api.spotify.com/v1/audio-features'

LIMIT_PER_RUN = 25

def get_audio_features_batch(track_ids):
    ids_string = ",".join(track_ids)
    response = requests.get(f"{BASE_URL}?ids={ids_string}", headers=HEADERS)
    if response.status_code != 200:
        print(f"Batch request failed: {response.status_code}")
        return []
    return response.json().get("audio_features", [])

def store_audio_features():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute('''
        SELECT track_id FROM Tracks
        WHERE track_id NOT IN (SELECT track_id FROM AudioFeatures)
        LIMIT ?
    ''', (LIMIT_PER_RUN,))
    track_ids = [row[0] for row in cur.fetchall()]
    print(f"Fetching audio features for {len(track_ids)} tracks...")

    features_list = get_audio_features_batch(track_ids)
    stored = 0

    for features in features_list:
        if features is None:
            continue
        cur.execute('''
            INSERT OR IGNORE INTO AudioFeatures (track_id, tempo, energy, loudness)
            VALUES (?, ?, ?, ?)
        ''', (
            features['id'],
            features['tempo'],
            features['energy'],
            features['loudness']
        ))
        print(f"Stored: {features['id']}")
        stored += 1
        time.sleep(0.1)

    conn.commit()
    conn.close()
    print(f"Done. Stored features for {stored} tracks.")

if __name__ == '__main__':
    store_audio_features()
