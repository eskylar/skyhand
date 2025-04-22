import sqlite3
import matplotlib.pyplot as plt
from collections import Counter

DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'

def bar_chart_avg_audio():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
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
    data = cur.fetchall()
    print("Data for bar chart:", data)
    conn.close()

    if not data:
        print("No data found for bar chart.")
        return

    labels = ['Unannotated', 'Annotated']
    features = ['Tempo', 'Energy', 'Loudness']

    x = range(len(features))
    has_annotations_map = {row[0]: row[1:] for row in data}
    values_unannotated = has_annotations_map.get(0, [0, 0, 0])
    values_annotated = has_annotations_map.get(1, [0, 0, 0])


    plt.figure()
    plt.bar(x, values_unannotated, width=0.4, label='Unannotated', align='center')
    plt.bar([i + 0.4 for i in x], values_annotated, width=0.4, label='Annotated', align='center')
    plt.xticks([i + 0.2 for i in x], features)
    plt.ylabel('Average Value')
    plt.title('Average Tempo, Energy, Loudness (Annotated vs Unannotated)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('bar_chart_audio_features.png')
    print("Saved bar_chart_audio_features.png")

def scatter_popularity_vs_annotations():
    """
    Create a scatter plot showing the relationship between Spotify popularity
    and Genius annotation count using join on artist.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = '''
        SELECT T.popularity, L.annotation_count
        FROM Lyrics L
        JOIN Tracks T ON L.artist_id = T.artist_id
        WHERE L.annotation_count > 0
    '''
    cur.execute(query)
    data = cur.fetchall()
    print("Data for scatter plot:", data)
    conn.close()

    popularity = [row[0] for row in data]
    annotations = [row[1] for row in data]

    plt.figure()
    plt.scatter(popularity, annotations, alpha=0.7)
    plt.title('Spotify Popularity vs. Genius Annotation Count (by artist)')
    plt.xlabel('Popularity (0–100)')
    plt.ylabel('Annotation Count')
    plt.tight_layout()
    plt.savefig('scatter_popularity_annotations.png')
    print("Saved scatter_popularity_annotations.png")

def pie_chart_annotated_genres():
    """
    Create a pie chart showing the distribution of genres among annotated songs
    using join on artist.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = '''
        SELECT T.genres
        FROM Lyrics L
        JOIN Tracks T ON L.artist_id = T.artist_id
        WHERE L.has_annotations = 1 AND T.genres IS NOT NULL
    '''
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    genres_counter = Counter()
    for (genres_str,) in rows:
        if not genres_str or not genres_str.strip():
            genres_counter["Unknown"] += 1
        else:
            genres = [g.strip() for g in genres_str.split(",") if g.strip()]
            if genres:
                genres_counter.update(genres)
            else:
                genres_counter["Unknown"] += 1

    most_common = genres_counter.most_common(6)
    print("Genre frequencies:", most_common)
    if not most_common:
        print("No genres data available for annotated songs.")
        return

    labels = [genre for genre, count in most_common]
    sizes = [count for genre, count in most_common]

    plt.figure()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Genres for Annotated Songs (by artist)')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('pie_chart_genres.png')
    print("Saved pie_chart_genres.png")

def line_chart_popularity_by_year():
    """
    Create a line chart showing average track popularity over time.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = '''
        SELECT SUBSTR(release_date, 1, 4) as year, AVG(popularity)
        FROM Tracks
        WHERE release_date IS NOT NULL AND LENGTH(release_date) >= 4
        GROUP BY year
        ORDER BY year
    '''
    cur.execute(query)
    data = cur.fetchall()
    conn.close()

    years = [int(row[0]) for row in data if row[0].isdigit()]
    avg_popularity = [row[1] for row in data if row[0].isdigit()]

    plt.figure()
    plt.plot(years, avg_popularity, marker='o')
    plt.title('Average Track Popularity by Release Year')
    plt.xlabel('Year')
    plt.ylabel('Avg Popularity')
    plt.tight_layout()
    plt.savefig('line_chart_popularity_by_year.png')
    print("Saved line_chart_popularity_by_year.png")

def histogram_track_loudness():
    """
    Create a histogram showing the distribution of track loudness.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = '''
        SELECT loudness
        FROM AudioFeatures
        WHERE loudness IS NOT NULL
    '''
    cur.execute(query)
    data = cur.fetchall()
    conn.close()

    loudness_values = [row[0] for row in data]

    plt.figure()
    plt.hist(loudness_values, bins=15, edgecolor='black')
    plt.title('Distribution of Track Loudness')
    plt.xlabel('Loudness (dB)')
    plt.ylabel('Number of Tracks')
    plt.tight_layout()
    plt.savefig('histogram_loudness.png')
    print("Saved histogram_loudness.png")

def run_all_viz():
    """
    Run all visualization functions sequentially to produce the bar, scatter, and pie charts.
    """
    bar_chart_avg_audio()
    scatter_popularity_vs_annotations()
    pie_chart_annotated_genres()
    line_chart_popularity_by_year()
    histogram_track_loudness()

if __name__ == '__main__':
    run_all_viz()