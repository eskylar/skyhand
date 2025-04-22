import sqlite3
import csv

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'

def connect_db():
    """
    Connect to the SQLite database and return the connection and cursor.

    Returns:
        tuple: (connection, cursor)
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    return conn, cur

def avg_audio_features_by_annotation():
    """
    Calculate the average tempo, energy, and loudness for annotated versus unannotated songs.

    Returns:
        list: Query results as a list of tuples.
    """
    conn, cur = connect_db()
    query = '''
    SELECT L.has_annotations,
        AVG(A.tempo),
        AVG(A.energy),
        AVG(A.loudness)
    FROM Lyrics L
    JOIN Tracks T ON INSTR(LOWER(T.name), LOWER(L.title)) > 0
    JOIN AudioFeatures A ON T.track_id = A.track_id
    JOIN Artists AR ON T.artist_id = AR.id
    WHERE L.artist_id = AR.id
    GROUP BY L.has_annotations
'''
    cur.execute(query)
    results = cur.fetchall()
    conn.close()
    return results

def get_popularity_and_annotations():
    """
    Retrieve Spotify popularity and Genius annotation count for songs with annotations.

    Returns:
        list: Query results as a list of tuples.
    """
    conn, cur = connect_db()
    query = '''
        SELECT T.popularity, L.annotation_count
        FROM Lyrics L
        JOIN Tracks T ON LOWER(L.title) = LOWER(T.name)
        JOIN Artists AR ON T.artist_id = AR.id
        WHERE L.artist_id = AR.id
          AND L.annotation_count > 0
    '''
    cur.execute(query)
    results = cur.fetchall()
    conn.close()
    return results

def write_summary_to_file(avg_features, pop_annots):
    """
    Write the analysis results to a CSV file.

    Args:
        avg_features (list): Averaged audio features data.
        pop_annots (list): Popularity and annotation count data.
    """
    with open('results_summary.csv', 'w', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(['--- Average Audio Features (0 = unannotated, 1 = annotated) ---'])
        writer.writerow(['Annotated?', 'Avg Tempo', 'Avg Energy', 'Avg Loudness'])
        for row in avg_features:
            writer.writerow(row)

        writer.writerow([])
        writer.writerow(['--- Popularity vs. Annotation Count ---'])
        writer.writerow(['Popularity', 'Annotation Count'])
        for row in pop_annots:
            writer.writerow(row)

    print("Saved analysis results to results_summary.csv")

def run_analysis():
    """
    Run all calculations and write the results to a file.
    """
    avg_features = avg_audio_features_by_annotation()
    pop_annots = get_popularity_and_annotations()
    write_summary_to_file(avg_features, pop_annots)

if __name__ == '__main__':
    run_analysis()

    #random change
