import psycopg2

# za kursor, koji ce vracat redove kao dict
from psycopg2.extras import RealDictCursor
from db import get_db_connection


def fetch_movies():
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT title, year FROM movies;")
        movies = cur.fetchall()
    conn.close()
    return movies


def search_movies_by_title(search, limit=10):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """SELECT title
            FROM movies
            WHERE title ILIKE %s 
            ORDER BY title 
            LIMIT %s;""",
            (f"%{search}%", limit),
        )
    results = cur.fetchall()
    return results
