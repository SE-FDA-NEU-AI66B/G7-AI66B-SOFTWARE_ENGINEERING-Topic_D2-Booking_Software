import os
import sqlite3

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SmartCine")
DB_PATH = os.environ.get("DB_PATH", "data/smartcine.db")


@app.get("/api/v1/recommendations")
def recommendations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, title, genre, rating FROM movie ORDER BY id LIMIT 10"
    ).fetchall()
    conn.close()

    
    html = "<h1>Recommendations (walking skeleton)</h1><table border='1'>"
    html += "<tr><th>ID</th><th>Title</th><th>Genre</th><th>Rating</th></tr>"
    for row in rows:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
    html += "</table>"
    return [dict(r) for r in rows]

# Serve the built React app. Must stay AFTER all API routes.
if os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", port=int(os.environ.get("PORT", "5000")), reload=True)