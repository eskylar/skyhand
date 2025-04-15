import sqlite3
import matplotlib.pyplot as plt
from collections import Counter

# Updated database path
DB_NAME = '/Users/skylaremerson/Desktop/SI206/skyhand/music_data.sqlite'

def bar_chart_popularity():
    """
    Create a bar chart comparing average track popularity between annotated
    and unannotated songs using data from the Tracks table.
    Uses a join that replaces 'é' with 'e' for improved matching.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Use REPLACE to fix accented characters in the join condition
    query = '''
        SELECT L.has_annotations, AVG(T.popularity)
        FROM Lyrics L
        JOIN Tracks T ON REPLACE(LOWER(L.artist), 'é', 'e') = REPLACE(LOWER(T.artist), 'é', 'e')
        GROUP BY L.has_annotations
    '''
    cur.execute(query)
    data = cur.fetchall()
    print("Data for popularity bar chart:", data)
    conn.close()

    pop_dict = {0: 0, 1: 0}
    for row in data:
        has_ann, avg_pop = row
        pop_dict[has_ann] = avg_pop

    labels = ['Unannotated', 'Annotated']
    pops = [pop_dict.get(0, 0), pop_dict.get(1, 0)]
    x = range(len(labels))

    plt.figure()
    plt.bar(x, pops, width=0.4, color='skyblue')
    plt.xticks(x, labels)
    plt.xlabel('Annotation Status')
    plt.ylabel('Average Popularity')
    plt.title('Average Popularity: Annotated vs. Unannotated Songs')
    plt.tight_layout()
    plt.savefig('bar_chart_popularity.png')
    print("Saved bar_chart_popularity.png")

def scatter_duration_vs_annotations():
    """
    Create a scatter plot showing the relationship between track duration and
    annotation count. Duration is converted from milliseconds to minutes.
    Uses a join that replaces 'é' with 'e' for improved matching.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = '''
         SELECT T.duration_ms, L.annotation_count
         FROM Lyrics L
         JOIN Tracks T ON REPLACE(LOWER(L.artist), 'é', 'e') = REPLACE(LOWER(T.artist), 'é', 'e')
         WHERE L.annotation_count > 0
    '''
    cur.execute(query)
    data = cur.fetchall()
    print("Data for duration scatter plot:", data)
    conn.close()

    if not data:
        print("No data for duration scatter plot.")
        return

    # Convert duration from ms to minutes
    durations = [row[0] / 60000 for row in data]
    annotations = [row[1] for row in data]

    plt.figure()
    plt.scatter(durations, annotations, alpha=0.7)
    plt.xlabel('Track Duration (minutes)')
    plt.ylabel('Annotation Count')
    plt.title('Track Duration vs. Annotation Count')
    plt.tight_layout()
    plt.savefig('scatter_duration_vs_annotations.png')
    print("Saved scatter_duration_vs_annotations.png")

def pie_chart_annotated_genres():
    """
    Create a pie chart showing the distribution of genres among annotated songs.
    Uses a join that replaces 'é' with 'e' for improved matching.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = '''
         SELECT T.genres
         FROM Lyrics L
         JOIN Tracks T ON REPLACE(LOWER(L.artist), 'é', 'e') = REPLACE(LOWER(T.artist), 'é', 'e')
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

def run_all_viz():
    """
    Run all visualization functions sequentially to produce:
      - A bar chart for average popularity,
      - A scatter plot for track duration vs. annotation count, and
      - A pie chart for annotated song genres.
    """
    bar_chart_popularity()
    scatter_duration_vs_annotations()
    pie_chart_annotated_genres()

if __name__ == '__main__':
    run_all_viz()
