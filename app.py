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


@app.get("/api/v1/recommendations")
def recommendations(_profile_id: int = Depends(get_current_profile)):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, title, genre, rating FROM movie ORDER BY id LIMIT 10"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]

# Serve the built React app. Must stay AFTER all API routes.
if os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", port=int(os.environ.get("PORT", "5000")), reload=True)