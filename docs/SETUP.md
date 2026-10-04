# SETUP

Follow these steps on a brand-new machine to run SmartCine's walking
skeleton (`GET /recommendations`).

## 1. Prerequisites

- Python 3.11 or newer
- pip (comes with Python)
- Git

Nothing else needs to be pre-installed.

## 2. Clone and install dependencies

**macOS / Linux:**
```bash
git clone https://github.com/<org>/<repo>.git
cd <repo>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```powershell
git clone https://github.com/<org>/<repo>.git
cd <repo>
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configuration

Copy `.env.example` to `.env`:

**macOS / Linux:** `cp .env.example .env`
**Windows:** `copy .env.example .env`

No values need to be changed — the defaults (`DB_PATH=data/smartcine.db`,
`PORT=5000`, `MOVIES_CSV=data/movies.csv`) are enough to run locally.

## 4. Create and seed the database

```bash
python init_db.py
```

This creates `data/smartcine.db` and seeds it with **12 rows** from
`data/movies.csv`. You should see:
```
Seeded 12 movies from data/movies.csv into data/smartcine.db
```

## 5. Run it and verify

```bash
python app.py
```

Open **http://localhost:5000/recommendations** in your browser.

**It worked if:** you see an HTML table with 10 rows, each showing a
movie ID, title, genre, and rating (e.g. "Oldboy", "Thriller", 8.4).

## 6. Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | The virtual environment isn't active. Re-run the `activate` command from step 2, then `pip install -r requirements.txt` again. |
| `OSError: [Errno 98] Address already in use` | Another process is using port 5000. Set `PORT=5001` in `.env`, then re-run `python app.py`. |
| `FileNotFoundError: data/movies.csv` | You're running the command from the wrong folder. Make sure you're in the project root (the folder containing `app.py`) before running `python init_db.py`. |

## 7. Tested by

- @<teammate username> (Team <NN>) on a fresh <Windows/macOS/Linux> machine, <date>, took <X> minutes.