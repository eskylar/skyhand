import sqlite3
import csv

DB_NAME = '/Users/skylaremerson/Desktop/SI206/Final Project/music_data.sqlite'


# ---------------------------------------------
# Connect to the database
# ---------------------------------------------
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    return conn, cur

# ---------------------------------------------
# 1. Calculate average audio features (annotated vs. unannotated)
# ---------------------------------------------
def avg_audio_features_by_annotation():
    conn, cur = connect_db()
    query = '''
        SELECT L.has_annotations, 
               AVG(A.tempo), 
               AVG(A.energy), 
               AVG(A.loudness)
        FROM Lyrics L
        JOIN Tracks T ON L.title = T.name AND L.artist = T.artist
        JOIN AudioFeatures A ON T.track_id = A.track_id
        GROUP BY L.has_annotations
    '''
    cur.execute(query)
    results = cur.fetchall()
    conn.close()
    return results

# ---------------------------------------------
# 2. Correlation-ish data: popularity vs. annotation count
# ---------------------------------------------
def get_popularity_and_annotations():
    conn, cur = connect_db()
    query = '''
        SELECT T.popularity, L.annotation_count
        FROM Lyrics L
        JOIN Tracks T ON L.title = T.name AND L.artist = T.artist
        WHERE L.annotation_count > 0
    '''
    cur.execute(query)
    results = cur.fetchall()
    conn.close()
    return results

# ---------------------------------------------
# 3. Save results to CSV
# ---------------------------------------------
def write_summary_to_file(avg_features, pop_annots):
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

# ---------------------------------------------
# Run all calculations
# ---------------------------------------------
def run_analysis():
    avg_features = avg_audio_features_by_annotation()
    pop_annots = get_popularity_and_annotations()
    write_summary_to_file(avg_features, pop_annots)

if __name__ == '__main__':
    run_analysis()
