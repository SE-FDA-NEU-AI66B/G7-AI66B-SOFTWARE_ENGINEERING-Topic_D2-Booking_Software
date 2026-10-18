import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from auth import get_conn, get_current_profile
from auth import router as auth_router
from profiles import router as profiles_router

load_dotenv()

app = FastAPI(title="SmartCine")
app.include_router(auth_router)
app.include_router(profiles_router)


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
    genre_id: str | None = None,
    _profile_id: int = Depends(get_current_profile),
):
    query = "SELECT id, title, genre, rating FROM movie WHERE rating >= 6.0"  # BR4
    params: tuple = ()
    if genre_id:
        query += " AND genre = ?"
        params = (genre_id,)
    query += " ORDER BY id LIMIT 10"  # BR3
    conn = get_conn()
    try:
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


# Serve the built React app. Must stay AFTER all API routes.
if os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", port=int(os.environ.get("PORT", "5000")), reload=True)