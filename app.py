import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from auth import get_conn, get_current_profile
from auth import router as auth_router
from profiles import router as profiles_router

load_dotenv()

app = FastAPI(title="SmartCine")
app.include_router(auth_router)
app.include_router(profiles_router)


class RatingRequest(BaseModel):
    movie_id: int
    score: int


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

MOVIE_COLUMNS = "id, title, genre, rating, rating_count, imdb_id"


def movie_exists(conn, movie_id: int) -> bool:
    row = conn.execute("SELECT 1 FROM movie WHERE id = ?", (movie_id,)).fetchone()
    return row is not None


def require_movie(conn, movie_id: int) -> None:
    if not movie_exists(conn, movie_id):
        raise HTTPException(status_code=404, detail="Movie not found.")


def mark_watched(conn, profile_id: int, movie_id: int) -> None:
    """Idempotent: marking the same movie twice does nothing the second time."""
    conn.execute(
        "INSERT OR IGNORE INTO watch_history (profile_id, movie_id) VALUES (?, ?)",
        (profile_id, movie_id),
    )


def not_watched_clause() -> str:
    """BR1: hide every movie this profile has watched (or rated).

    Both recommendation queries below use this one clause. The query needs the
    named parameter :profile_id, which is always supplied.

    MUTATION CHECK (tests/test_ratings_watch.py): to prove the tests can fail,
    make this function return "1 = 1", run pytest, then restore it. Nothing
    else has to change, because parameters are named and extra ones are ignored.
    """
    # return "1=1"  ''' test xem nó trả lỗi bằng cách uncomment cái này'''
    return (
        "NOT EXISTS (SELECT 1 FROM watch_history w "
        "WHERE w.profile_id = :profile_id AND w.movie_id = movie.id)"
    )


# ---------------------------------------------------------------------------
# Movies, ratings, watch history
# ---------------------------------------------------------------------------


@app.get("/api/v1/movies/{movie_id}")
def get_movie(movie_id: int, _profile_id: int = Depends(get_current_profile)):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT m.id, m.title, m.genre, m.rating, m.rating_count, m.imdb_id, "
            "r.score AS user_rating, "
            "EXISTS (SELECT 1 FROM watch_history w "
            "WHERE w.profile_id = ? AND w.movie_id = m.id) AS watched "
            "FROM movie m LEFT JOIN rating r "
            "ON r.movie_id = m.id AND r.profile_id = ? WHERE m.id = ?",
            (_profile_id, _profile_id, movie_id),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Movie not found.")
    data = dict(row)
    data["watched"] = bool(data["watched"])
    return data


@app.post("/api/v1/ratings", status_code=201)
def save_rating(body: RatingRequest, profile_id: int = Depends(get_current_profile)):
    if not 1 <= body.score <= 10:
        raise HTTPException(
            status_code=400, detail="Rating must be between 1 and 10."
        )

    conn = get_conn()
    try:
        require_movie(conn, body.movie_id)
        conn.execute(
            "INSERT INTO rating (profile_id, movie_id, score) VALUES (?, ?, ?) "
            "ON CONFLICT(profile_id, movie_id) DO UPDATE SET score = excluded.score",
            (profile_id, body.movie_id, body.score),
        )
        mark_watched(conn, profile_id, body.movie_id)  # rating also marks watched
        conn.commit()
    finally:
        conn.close()
    return {"movie_id": body.movie_id, "score": body.score}


@app.post("/api/v1/movies/{movie_id}/watch")
def mark_movie_watched(movie_id: int, profile_id: int = Depends(get_current_profile)):
    conn = get_conn()
    try:
        require_movie(conn, movie_id)
        mark_watched(conn, profile_id, movie_id)
        conn.commit()
    finally:
        conn.close()
    return {"movie_id": movie_id, "watched": True}


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------


@app.get("/api/v1/recommendations/setup/genres")
def get_recommendation_genres(_profile_id: int = Depends(get_current_profile)):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT DISTINCT genre AS id, genre AS name FROM movie "
            "WHERE genre IS NOT NULL AND genre != '' ORDER BY genre"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def count_preferences(conn, profile_id: int) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM ("
        "SELECT movie_id FROM rating WHERE profile_id = :profile_id "
        "UNION SELECT movie_id FROM watch_history WHERE profile_id = :profile_id"
        ")",
        {"profile_id": profile_id},
    ).fetchone()[0]


def cold_start_recommendations(conn, profile_id: int, genre_id: str | None):
    """BR5 / BR6: top-rated movies with at least 100 ratings, not yet watched."""
    query = (
        f"SELECT {MOVIE_COLUMNS} FROM movie "
        f"WHERE rating_count >= 100 AND {not_watched_clause()}"
    )
    params = {"profile_id": profile_id}
    if genre_id:
        query += " AND genre = :genre_id"
        params["genre_id"] = genre_id
    query += " ORDER BY rating DESC, rating_count DESC, id LIMIT 10"
    return conn.execute(query, params).fetchall()


def personalized_recommendations(conn, profile_id: int, genre_id: str | None):
    """BR3, BR4, BR9 (partial): good movies, favouring the profile's best genres."""
    query = (
        f"SELECT {MOVIE_COLUMNS} FROM movie "
        f"WHERE rating >= 6.0 AND {not_watched_clause()}"  # BR4
    )
    params = {"profile_id": profile_id}
    if genre_id:
        query += " AND genre = :genre_id"
        params["genre_id"] = genre_id
    query += (
        " ORDER BY (SELECT COALESCE(AVG(r.score), 0) FROM rating r "
        "JOIN movie m2 ON m2.id = r.movie_id "
        "WHERE r.profile_id = :profile_id AND m2.genre = movie.genre) DESC, "
        "rating DESC, rating_count DESC, id LIMIT 10"  # BR3
    )
    return conn.execute(query, params).fetchall()


@app.get("/api/v1/recommendations")
def recommendations(
    response: Response,
    genre_id: str | None = None,
    _profile_id: int = Depends(get_current_profile),
):
    conn = get_conn()
    try:
        if count_preferences(conn, _profile_id) < 5:  # BR5 / BR6
            rows = cold_start_recommendations(conn, _profile_id, genre_id)
            if len(rows) < 10:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "code": "COLD_START_UNAVAILABLE",
                        "message": "Fewer than 10 movies have at least 100 ratings.",
                    },
                )
            response.headers["X-Recommendation-Mode"] = "cold-start"
        else:
            rows = personalized_recommendations(conn, _profile_id, genre_id)
            response.headers["X-Recommendation-Mode"] = "personalized"
    finally:
        conn.close()
    return [dict(r) for r in rows]


# Serve the built React app. Must stay AFTER all API routes.
if os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", port=int(os.environ.get("PORT", "5000")), reload=True)