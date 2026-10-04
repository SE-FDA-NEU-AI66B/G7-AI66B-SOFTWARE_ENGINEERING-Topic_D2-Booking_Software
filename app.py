import os
import sqlite3

from flask import Flask

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "data/smartcine.db")


@app.route("/recommendations")
def recommendations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, genre, rating FROM movie ORDER BY id LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    # No CSS, no styling, no real UI yet - just prove the data is real.
    html = "<h1>Recommendations (walking skeleton)</h1><table border='1'>"
    html += "<tr><th>ID</th><th>Title</th><th>Genre</th><th>Rating</th></tr>"
    for row in rows:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
    html += "</table>"
    return html


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=True, port=port)
