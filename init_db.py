import csv
import os
import sqlite3

from dotenv import load_dotenv

from auth import ensure_schema_and_seed

load_dotenv()

DB_PATH = os.environ.get("DB_PATH", "data/smartcine.db")
CSV_PATH = os.environ.get("MOVIES_CSV", "data/movies.csv")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS movie")
cursor.execute(
    """
    CREATE TABLE movie (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        genre TEXT NOT NULL,
        rating REAL NOT NULL,
        rating_count INTEGER NOT NULL CHECK (rating_count >= 0),
        imdb_id TEXT NOT NULL UNIQUE
    )
    """
)

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    movies = [
        (
            int(row["id"]),
            row["title"],
            row["genre"],
            float(row["rating"]),
            int(row["rating_count"]),
            row["imdb_id"],
        )
        for row in reader
    ]

cursor.executemany(
    "INSERT INTO movie (id, title, genre, rating, rating_count, imdb_id) "
    "VALUES (?, ?, ?, ?, ?, ?)",
    movies,
)

cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS rating (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER NOT NULL REFERENCES profile(id),
        movie_id INTEGER NOT NULL REFERENCES movie(id),
        score INTEGER NOT NULL CHECK (score BETWEEN 1 AND 10),
        UNIQUE (profile_id, movie_id)
    );
    CREATE TABLE IF NOT EXISTS watch_history (
        profile_id INTEGER NOT NULL REFERENCES profile(id),
        movie_id INTEGER NOT NULL REFERENCES movie(id),
        PRIMARY KEY (profile_id, movie_id)
    );
    """
)

ensure_schema_and_seed(conn)

conn.commit()
conn.close()

print(f"Seeded {len(movies)} movies from {CSV_PATH} into {DB_PATH}")