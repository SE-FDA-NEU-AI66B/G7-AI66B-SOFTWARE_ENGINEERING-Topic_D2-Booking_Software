import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_MOVIES = 42
MIN_PER_GENRE = 14


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
    """Run the real seed script once, into a temporary file."""
    path = tmp_path_factory.mktemp("seed") / "smartcine.db"
    env = {
        **os.environ,
        "DB_PATH": str(path),
        "MOVIES_CSV": "data/movies.csv",  
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
    }
    result = subprocess.run(
        [sys.executable, "init_db.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, f"init_db.py failed:\n{result.stderr}"
    return path


@pytest.fixture()
def conn(db_path):
    """A connection whose changes are rolled back, so tests do not affect each other."""
    connection = sqlite3.connect(db_path)
    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()


def first_profile_id(conn):
    return conn.execute("SELECT id FROM profile ORDER BY id LIMIT 1").fetchone()[0]


# --- Seed data -------------------------------------------------------------


def test_tc25_seed_loads_all_movies(conn):
    count = conn.execute("SELECT COUNT(*) FROM movie").fetchone()[0]
    assert count == EXPECTED_MOVIES


def test_tc26_every_genre_has_at_least_14_movies(conn):
    rows = conn.execute("SELECT genre, COUNT(*) FROM movie GROUP BY genre").fetchall()
    assert {genre for genre, _ in rows} == {"Horror", "Romance", "Thriller"}
    for genre, count in rows:
        assert count >= MIN_PER_GENRE, f"{genre} has only {count} movies"


def test_tc27_every_movie_has_at_least_100_votes(conn):
    below = conn.execute("SELECT COUNT(*) FROM movie WHERE rating_count < 100").fetchone()[0]
    assert below == 0


def test_tc28_duplicate_imdb_id_is_rejected(conn):
    existing = conn.execute("SELECT imdb_id FROM movie LIMIT 1").fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO movie (id, title, genre, rating, rating_count, imdb_id) "
            "VALUES (9999, 'Copy', 'Horror', 7.0, 500, ?)",
            (existing,),
        )


# --- Constraints -----------------------------------------------------------


@pytest.mark.parametrize(
    "score, accepted",
    [
        (0, False),   # just below the lowest score
        (1, True),    # lowest allowed score
        (10, True),   # highest allowed score
        (11, False),  # just above the highest score
    ],
)
def test_tc29_rating_score_limits(conn, score, accepted):
    profile_id = first_profile_id(conn)
    sql = "INSERT INTO rating (profile_id, movie_id, score) VALUES (?, 1, ?)"
    if accepted:
        conn.execute(sql, (profile_id, score))
    else:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(sql, (profile_id, score))


def test_tc30_same_profile_cannot_rate_a_movie_twice(conn):
    profile_id = first_profile_id(conn)
    conn.execute("INSERT INTO rating (profile_id, movie_id, score) VALUES (?, 1, 7)", (profile_id,))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO rating (profile_id, movie_id, score) VALUES (?, 1, 9)", (profile_id,)
        )


def test_tc31_same_profile_cannot_watch_a_movie_twice(conn):
    profile_id = first_profile_id(conn)
    conn.execute("INSERT INTO watch_history (profile_id, movie_id) VALUES (?, 1)", (profile_id,))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO watch_history (profile_id, movie_id) VALUES (?, 1)", (profile_id,))