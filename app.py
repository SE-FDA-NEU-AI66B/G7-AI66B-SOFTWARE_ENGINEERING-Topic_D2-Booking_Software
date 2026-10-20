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
        exists = conn.execute(
            "SELECT 1 FROM movie WHERE id = ?", (body.movie_id,)
        ).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="Movie not found.")
        conn.execute(
            "INSERT INTO rating (profile_id, movie_id, score) VALUES (?, ?, ?) "
            "ON CONFLICT(profile_id, movie_id) DO UPDATE SET score = excluded.score",
            (profile_id, body.movie_id, body.score),
        )
        conn.execute(
            "INSERT OR IGNORE INTO watch_history (profile_id, movie_id) VALUES (?, ?)",
            (profile_id, body.movie_id),
        )
        conn.commit()
    finally:
        conn.close()
    return {"movie_id": body.movie_id, "score": body.score}


@app.post("/api/v1/movies/{movie_id}/watch")
def mark_movie_watched(movie_id: int, profile_id: int = Depends(get_current_profile)):
    conn = get_conn()
    try:
        exists = conn.execute(
            "SELECT 1 FROM movie WHERE id = ?", (movie_id,)
        ).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="Movie not found.")
        conn.execute(
            "INSERT OR IGNORE INTO watch_history (profile_id, movie_id) VALUES (?, ?)",
            (profile_id, movie_id),
        )
        conn.commit()
    finally:
        conn.close()
    return {"movie_id": movie_id, "watched": True}


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


@app.get("/api/v1/recommendations")
def recommendations(
    response: Response,
    genre_id: str | None = None,
    _profile_id: int = Depends(get_current_profile),
):
    conn = get_conn()
    try:
        preference_count = conn.execute(
            "SELECT COUNT(*) FROM ("
            "SELECT movie_id FROM rating WHERE profile_id = ? "
            "UNION SELECT movie_id FROM watch_history WHERE profile_id = ?"
            ")",
            (_profile_id, _profile_id),
        ).fetchone()[0]

        if preference_count < 5:  # BR5 / BR6
            rows = conn.execute(
                "SELECT id, title, genre, rating, rating_count, imdb_id FROM movie "
                "WHERE rating_count >= 100 AND NOT EXISTS ("
                "SELECT 1 FROM watch_history w "
                "WHERE w.profile_id = ? AND w.movie_id = movie.id) "
                "ORDER BY rating DESC, rating_count DESC, id LIMIT 10",
                (_profile_id,),
            ).fetchall()
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
            query = (
                "SELECT id, title, genre, rating, rating_count, imdb_id "
                "FROM movie WHERE rating >= 6.0 AND NOT EXISTS ("
                "SELECT 1 FROM watch_history w "
                "WHERE w.profile_id = ? AND w.movie_id = movie.id)"
            )  # BR4
            params = (_profile_id,)
            if genre_id:
                query += " AND genre = ?"
                params = (_profile_id, genre_id)

            query += (
                " ORDER BY (SELECT COALESCE(AVG(r.score), 0) FROM rating r "
                "JOIN movie m2 ON m2.id = r.movie_id "
                "WHERE r.profile_id = ? AND m2.genre = movie.genre) DESC, "
                "rating DESC, rating_count DESC, id LIMIT 10"  # BR3, BR9 (partial)
            )
            params = (*params, _profile_id)
            rows = conn.execute(query, params).fetchall()    
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