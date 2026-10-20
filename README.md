# SmartCine

SmartCine is a movie recommendation web app that answers "what should I watch next?". Choose a profile, pick a genre, and get up to 10 movies. New profiles see trending movies right away; once a profile has rated or watched 5 movies, the list is ranked by the genres it rates highest and hides movies it has already watched.

## Team

| Name | GitHub username | Role |
| --- | --- | --- |
| Hoang Thi Phuong Linh | phuonglinhtla | Member |
| Nguyen Quang Huy | KatsuroHuy | Product Owner |
| Nguyen Vinh Hung | Nvhwng | Member |
| Be Thanh Dat | th3dummyking | Member |

Scrum Master: @KatsuroHuy (Sprint 1), @th3dummyking (Sprint 2), @Nvhwng (Sprint 3), @phuonglinhtla (Sprint 4)
Board: https://github.com/orgs/SE-FDA-NEU-AI66B/projects/9
Setup Guide: https://github.com/SE-FDA-NEU-AI66B/G7-AI66B-SOFTWARE_ENGINEERING-Topic_D2-Booking_Software/blob/main/docs/SETUP.md

## Setup

Full steps for macOS, Linux and Windows are in [docs/SETUP.md](docs/SETUP.md). In short:

```bash
git clone https://github.com/SE-FDA-NEU-AI66B/G7-AI66B-SOFTWARE_ENGINEERING-Topic_D2-Booking_Software.git
cd G7-AI66B-SOFTWARE_ENGINEERING-Topic_D2-Booking_Software
```

Then create a virtual environment, install the requirements, build the frontend, seed the database with `python init_db.py` and start the app with `python app.py`.


## Try it

Run the app with the [Setup guide](docs/SETUP.md), then open <http://localhost:5000/>.

**Test account:** `demo@smartcine.test` / `Demo@1234` (two profiles: Alex and Sam)

**P0 stories and where each starts:**

| Story | Where it starts |
|---|---|
| US10 — Select a profile before watching | Sign in at `/#/login`, then you land on `/#/profiles` |
| US06 — Ask for a theme before recommending | `/#/recommendations/setup` (opens after choosing a profile) |
| US01 — Cold-start recommendations | Press **Get recommendations** on the setup page (`/#/recommendations`) |
| US03 — Personalized recommendations | Same page, after the profile has rated or watched 5 movies |
| US02 — Rate a watched movie | Click a movie title in the list (`/#/movie/:id`) |
| US04 — Exclude watched movies | Press **Mark as watched** or rate a movie; it disappears from the list |

Full status of every story: [docs/ui.md](docs/ui.md).