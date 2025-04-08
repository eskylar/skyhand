import sqlite3
import matplotlib.pyplot as plt

DB_NAME = '/Users/skylaremerson/Desktop/SI206/Final Project/music_data.sqlite'

# ---------------------------------------------
# Create Lyrics table (if not exists)
# ---------------------------------------------
def create_lyrics_table():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Lyrics (
            title TEXT,
            artist TEXT,
            has_annotations INTEGER,
            annotation_count INTEGER,
            PRIMARY KEY (title, artist)
        )
    ''')
    conn.commit()
    conn.close()

# ---------------------------------------------
# Bar chart: Avg audio features (annotated vs. unannotated)
# ---------------------------------------------
def bar_chart_avg_audio():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = '''
        SELECT L.has_annotations, AVG(A.tempo), AVG(A.energy), AVG(A.loudness)
        FROM Lyrics L
        JOIN Tracks T ON L.title = T.name AND L.artist = T.artist
        JOIN AudioFeatures A ON T.track_id = A.track_id
        GROUP BY L.has_annotations
    '''
    cur.execute(query)
    data = cur.fetchall()
    print("Data for bar chart:", data)  # Add this to debug the query result
    conn.close()

    # Initialize values
    tempo_dict = {0: 0, 1: 0}
    energy_dict = {0: 0, 1: 0}
    loudness_dict = {0: 0, 1: 0}

    # Fill from query result
    for row in data:
        has_ann = row[0]
        tempo_dict[has_ann] = row[1]
        energy_dict[has_ann] = row[2]
        loudness_dict[has_ann] = row[3]

    # Always use both keys for consistent bar sizes
    labels = ['Unannotated', 'Annotated']
    tempos = [tempo_dict[0], tempo_dict[1]]
    energies = [energy_dict[0], energy_dict[1]]
    loudness = [loudness_dict[0], loudness_dict[1]]

    x = range(len(labels))

    plt.figure()
    plt.bar(x, tempos, width=0.2, label='Tempo', align='center')
    plt.bar([i + 0.2 for i in x], energies, width=0.2, label='Energy', align='center')
    plt.bar([i + 0.4 for i in x], loudness, width=0.2, label='Loudness', align='center')
    plt.xticks([i + 0.2 for i in x], labels)
    plt.title('Avg Audio Features: Annotated vs. Unannotated Songs')
    plt.xlabel('Annotation Status')
    plt.ylabel('Value')
    plt.legend()
    plt.tight_layout()
    plt.savefig('bar_chart_audio_features.png')
    print("Saved bar_chart_audio_features.png")


# ---------------------------------------------
# Scatter plot: Popularity vs. Annotation Count
# ---------------------------------------------
def scatter_popularity_vs_annotations():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = '''
        SELECT T.popularity, L.annotation_count
        FROM Lyrics L
        JOIN Tracks T ON L.title = T.name AND L.artist = T.artist
        WHERE L.annotation_count > 0
    '''
    cur.execute(query)
    data = cur.fetchall()
    print(f"Data for scatter plot: {data}")
    conn.close()

    popularity = [row[0] for row in data]
    annotations = [row[1] for row in data]

    plt.figure()
    plt.scatter(popularity, annotations, alpha=0.7)
    plt.title('Spotify Popularity vs. Genius Annotation Count')
    plt.xlabel('Popularity (0–100)')
    plt.ylabel('Annotation Count')
    plt.tight_layout()
    plt.savefig('scatter_popularity_annotations.png')
    print("Saved scatter_popularity_annotations.png")

# ---------------------------------------------
# Pie chart: Most common artists among annotated songs
# ---------------------------------------------
def pie_chart_annotated_artists():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = '''
        SELECT L.artist, COUNT(*)
        FROM Lyrics L
        WHERE L.has_annotations = 1
        GROUP BY L.artist
        ORDER BY COUNT(*) DESC
        LIMIT 6
    '''
    cur.execute(query)
    data = cur.fetchall()
    conn.close()
    print("Data from query:", data)

    labels = [row[0] for row in data]
    sizes = [row[1] for row in data]

    plt.figure()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Most Common Artists (Annotated Songs)')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('pie_chart_artists.png')
    print("Saved pie_chart_artists.png")

# ---------------------------------------------
# Run all visualizations
# ---------------------------------------------
def run_all_viz():
    create_lyrics_table()
    bar_chart_avg_audio()
    scatter_popularity_vs_annotations()
    pie_chart_annotated_artists()

if __name__ == '__main__':
    run_all_viz()
