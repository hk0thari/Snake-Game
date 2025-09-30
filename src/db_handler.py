import sqlite3


# Connection to the database
def connect_database(path):
    conn = None
    try:
        conn = sqlite3.connect(path)
        # Create the scores table if it doesn't exist
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            snake_speed TEXT,
            board_size TEXT,
            score INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.close()
        conn = None
        cursor = None

    return conn, cursor


# Function to get data from the database
def get_scores_data(snake_speed="Slow", board_size="Small", group_by_player_name=False):
    conn, cursor = connect_database("snake_game.db")
    if not conn:
        print("No connection")
        return [], [], []

    try:
        if group_by_player_name:
            query = f"""
            SELECT id, player_name, score
            FROM scores
            WHERE snake_speed = '{snake_speed}' AND board_size = '{board_size}'
            AND (player_name, score) IN (
                SELECT player_name, MAX(score)
                FROM scores
                WHERE snake_speed = '{snake_speed}' AND board_size = '{board_size}'
                GROUP BY player_name
                )
            ORDER BY score DESC
            LIMIT 100;"""
        else:
            query = f"""
            SELECT id, player_name, score
            FROM scores
            WHERE snake_speed = '{snake_speed}' AND board_size = '{board_size}'
            ORDER BY date DESC
            LIMIT 100"""

        cursor.execute(query)

        rows = cursor.fetchall()
        ids = [row[0] for row in rows]
        player_names = [row[1] for row in rows]
        scores = [row[2] for row in rows]
        return player_names, scores, ids

    except sqlite3.Error as e:
        print(f"Query error: {e}")
        return [], [], []

    finally:
        conn.close()


def save_score(cursor, conn, player_name, snake_speed, board_size, score):
    cursor.execute('INSERT INTO scores (player_name, score, snake_speed, board_size) VALUES (?, ?, ?, ?)',
                   (player_name, score, snake_speed, board_size))
    conn.commit()
    cursor.execute('SELECT * FROM scores')
