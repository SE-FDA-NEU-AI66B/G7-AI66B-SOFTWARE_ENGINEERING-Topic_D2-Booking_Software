# SETUP

Follow these steps on a brand-new machine to run SmartCine: sign in, choose a profile, and see the movie recommendations.

## 1. Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer (includes npm)
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

Build the frontend (both systems):
```bash
cd frontend
npm install
npm run build
cd ..
```

## 3. Configuration

Copy `.env.example` to `.env`:

**macOS / Linux:** `cp .env.example .env`
**Windows:** `copy .env.example .env`

No values need to be changed — the defaults (`DB_PATH=data/smartcine.db`,`PORT=5000`, `MOVIES_CSV=data/movies.csv`) are enough to run locally.
`JWT_SECRET` is the key that signs login tokens; the placeholder in
`.env.example` is fine for local use. Never commit your `.env` file.

## 4. Create and seed the database

```bash
python init_db.py
```

This creates `data/smartcine.db` and seeds it with **12 movies** from `data/movies.csv`, plus one test account with two profiles (see [Test account](#test-account)). You should see:
```
Seeded 12 movies from data/movies.csv into data/smartcine.db
```

## 5. Run it and verify

```bash
python app.py
```

Open **http://localhost:5000/** in your browser.
The API documentation is at http://localhost:5000/docs.

**It worked if:**
1. You see the SmartCine sign-in page.
2. Signing in with the [test account](#test-account) shows "Who's watching?" with two profiles, Alex and Sam.
3. Choosing a profile opens the recommendations setup page; its "See recommendations" button shows a table with 10 movies, each with an ID, title, genre, and rating (e.g. "Oldboy", "Thriller", 8.4).
4. Signing in with a wrong password shows "The email or password is incorrect."

## 6. Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` (or `'jwt'`) | The virtual environment isn't active. Re-run the `activate` command from step 2, then `pip install -r requirements.txt` again. |
| `OSError: [Errno 98] Address already in use` | Another process is using port 5000. Set `PORT=5001` in `.env`, then re-run `python app.py`. |
| `FileNotFoundError: data/movies.csv` | You're running the command from the wrong folder. Make sure you're in the project root (the folder containing `app.py`) before running `python init_db.py`. |
| `npm: command not found` | Install Node.js 20+ from nodejs.org, reopen the terminal, then repeat the frontend build step. |
| Page shows `{"detail":"Not Found"}` | `frontend/dist` doesn't exist yet. Run `npm run build` inside `frontend/`, then restart `python app.py`. |
| The page is blank, shows an old version, or says "We can't reach the server" after signing in | The frontend build is outdated. Run `npm run build` inside `frontend/`, then hard-refresh the browser (Ctrl+F5, or Cmd+Shift+R on macOS). |
| Sign-in fails with the test account | Run `python init_db.py` again to restore the test account, then restart `python app.py`. |
| `ModuleNotFoundError: No module named 'auth'` when running `pytest` | Run `pytest` from the project root (the folder containing `app.py` and `pytest.ini`) with the virtual environment active. |

## 7. Test account

| Email | Password | Profiles |
|---|---|---|
| demo@smartcine.test | Demo@1234 | Alex, Sam |

Created by `python init_db.py`. For local testing only; these are fake credentials.

## 8. Run the checks (optional)

```bash
ruff check .
pytest
cd frontend
npm run lint
npm run build
```

## 9. Tested by

- @th3dummyking (Team 07) on a fresh Windows machine, 4/10/2026, took 15 minutes.
- <name> on <OS>, <date>, <duration>, Sprint 3 (sign-in and profile selection).