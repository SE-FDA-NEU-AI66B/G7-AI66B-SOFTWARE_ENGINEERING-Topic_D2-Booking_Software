import csv
import os
import sqlite3

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
        rating REAL NOT NULL
    )
    """
)

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    movies = [
        (int(row["id"]), row["title"], row["genre"], float(row["rating"]))
        for row in reader
    ]

cursor.executemany(
    "INSERT INTO movie (id, title, genre, rating) VALUES (?, ?, ?, ?)", movies
)

conn.commit()
conn.close()

print(f"Seeded {len(movies)} movies from {CSV_PATH} into {DB_PATH}")