## 1. P0 stories and status
 
Status reflects what is on `main` at submission time. "Works" means the user can complete the story through the UI with real data. "Partly works" means the screen exists but one acceptance criterion is incomplete.
 
| Story | Screen(s) | Route(s) | Status | Issue |
|---|---|---|---|---|
| US10 — Select a profile before watching | Sign in, Who's watching? | `/login` → `/profiles` | Works | [#32](https://github.com/SE-FDA-NEU-AI66B/G7-AI66B-SOFTWARE_ENGINEERING-Topic_D2-Booking_Software/issues/32) |
| US06 — Ask for a theme before recommending | Genre picker | `/recommendations/setup` | Partly works — the genre filter only applies once a profile has 5 or more rated or watched movies; the cold-start list ignores it | [#27](https://github.com/SE-FDA-NEU-AI66B/G7-AI66B-SOFTWARE_ENGINEERING-Topic_D2-Booking_Software/issues/27), [#28](https://github.com/SE-FDA-NEU-AI66B/G7-AI66B-SOFTWARE_ENGINEERING-Topic_D2-Booking_Software/issues/28) |
| US01 — Cold-start recommendations | Recommendation list | `/recommendations` | Works | [#23](https://github.com/SE-FDA-NEU-AI66B/G7-AI66B-SOFTWARE_ENGINEERING-Topic_D2-Booking_Software/issues/23) |
| US03 — Personalized recommendations | Recommendation list | `/recommendations` | Works — genres the profile rates highest are listed first | [#25](https://github.com/SE-FDA-NEU-AI66B/G7-AI66B-SOFTWARE_ENGINEERING-Topic_D2-Booking_Software/issues/25) |
| US02 — Rate a watched movie | Movie detail | `/movie/:id` | Works | [#24](https://github.com/SE-FDA-NEU-AI66B/G7-AI66B-SOFTWARE_ENGINEERING-Topic_D2-Booking_Software/issues/24) |
| US04 — Exclude watched movies | Movie detail, recommendation list | `/movie/:id` → `/recommendations` | Works | [#26](https://github.com/SE-FDA-NEU-AI66B/G7-AI66B-SOFTWARE_ENGINEERING-Topic_D2-Booking_Software/issues/26) |
 
Screens outside the P0 stories:
 
| Route | Status |
|---|---|
| `/` (landing page) | Not started — signed-out visitors are redirected to `/login` |
| `/profile/ratings` (P1) | Not started — the route is not registered |
 
### Screen flow
 
```mermaid
flowchart TD
    A[Open SmartCine] --> B["/login"]
    B -->|Sign in succeeds| C["/profiles"]
    C -->|Choose a profile| D["/recommendations/setup"]
    D -->|Pick a genre, Continue| E["/recommendations?genre_id=..."]
    D -->|Get recommendations| F["/recommendations"]
    E --> G[Select a movie title]
    F --> G
    G --> H["/movie/:id"]
    H -->|Save or update rating| H
    H -->|Mark as watched| H
    H -->|Back to recommendations| F
    F -->|Switch profile| C
    C -->|Sign out| B
```
 
Routes use hash URLs (for example `#/profiles`). A visitor without a session is sent to `/login`; a signed-in user without a chosen profile is sent to `/profiles`.
 
---


## 2. Wireframes
 
Every screen is drawn as plain text. `[ ]` is a button, `( )` is a selectable option, `…` marks loading text.
 
### 2.1 `/login` — Sign in
 
**The user comes here to:** sign in with an email and password.
 
**Calls:** `POST /api/v1/auth/login`
 
```
+--------------------------------------------------+
|                    SmartCine                     |
|                                                  |
|   Sign in                                        |
|   Email     [ demo@smartcine.test            ]   |
|   Password  [ ••••••••                [Show] ]   |
|                                                  |
|   [ Sign in ]                                    |
+--------------------------------------------------+
 
While waiting:  the button reads  [ Signing in… ]  and is disabled
On error:       a red message appears above the button (see section 3)
```
 
### 2.2 `/profiles` — Who's watching?
 
**The user comes here to:** choose which profile of the account is watching, so ratings and watched movies are kept per person.
 
**Calls:** `GET /api/v1/profiles`, `POST /api/v1/profiles/select`
 
This screen is shown in all four states.
 
```
DATA                                   LOADING
+--------------------------------+     +--------------------------------+
|           SmartCine            |     |           SmartCine            |
|        Who's watching?         |     |        Who's watching?         |
|                                |     |                                |
|    ( A )          ( S )        |     |        Loading profiles…       |
|    Alex           Sam          |     |                                |
|                                |     |        Sign out                |
|        Sign out                |     +--------------------------------+
+--------------------------------+
 
EMPTY                                  ERROR
+--------------------------------+     +--------------------------------+
|           SmartCine            |     |           SmartCine            |
|        Who's watching?         |     |        Who's watching?         |
|                                |     |                                |
|  This account has no profiles  |     |  We can't load your profiles.  |
|  yet.                          |     |  [ Try again ]                 |
|                                |     |                                |
|        Sign out                |     |        Sign out                |
+--------------------------------+     +--------------------------------+
```
 
### 2.3 `/recommendations/setup` — Genre picker
 
**The user comes here to:** say what they are in the mood for before seeing a list.
 
**Calls:** `GET /api/v1/recommendations/setup/genres`
 
```
+----------------------------------------------------------+
| SmartCine                     (A) Alex  Switch profile   |
|                                                Sign out  |
+----------------------------------------------------------+
|                                                          |
|   What are you in the mood for?                          |
|                                                          |
|   ( Horror )   ( Romance )   ( Thriller )                |
|                                                          |
|   [ Continue ]        [ Get recommendations ]            |
|   Pick a genre to continue.                              |
+----------------------------------------------------------+
 
Loading:  "Loading genres…"
Error:    "We can't load the genres.  [ Try again ]"
Empty:    "No genres are available yet. Please check back later."
```
 
Continue stays disabled until a genre is chosen. **Get recommendations** skips the genre.
 
### 2.4 `/recommendations` — Recommendation list
 
**The user comes here to:** see up to 10 movies worth watching and open one.
 
**Calls:** `GET /api/v1/recommendations` (optional `genre_id`); the response header `X-Recommendation-Mode` is `cold-start` or `personalized`.
 
This screen is shown in all four states, plus the cold-start variant.
 
```
DATA (personalized)
+----------------------------------------------------------+
| SmartCine                     (A) Alex  Switch profile   |
+----------------------------------------------------------+
|  Picked for you: Horror                                  |
|  Change genre                                            |
|                                                          |
|  Title            Genre     IMDb rating   IMDb votes     |
|  ------------------------------------------------------  |
|  The Shining      Horror    8.4/10        1,248,440      |
|  Get Out          Horror    7.8/10          842,084      |
|  ... up to 10 rows, each title opens /movie/:id          |
+----------------------------------------------------------+
 
DATA (cold-start: fewer than 5 rated or watched movies)
+----------------------------------------------------------+
|  Trending recommendations                                |
|  Change genre                                            |
|  Rate or watch at least 5 movies to get picks matched    |
|  to your taste. Until then, these are the most-voted     |
|  movies for everyone.                                    |
|  (same table, exactly 10 rows, each with 100+ votes)     |
+----------------------------------------------------------+
 
LOADING                         EMPTY
+---------------------------+   +--------------------------------+
|  Loading                  |   |  No movies found for "Horror". |
|  recommendations...       |   |  Choose another genre          |
+---------------------------+   +--------------------------------+
 
ERROR (server unreachable)      ERROR (cold-start list unavailable)
+---------------------------+   +--------------------------------+
|  We can't reach the       |   |  No movies currently qualify   |
|  server. [ Try again ]    |   |  for the cold-start list (at   |
+---------------------------+   |  least 100 ratings).           |
                                |  Try again later               |
                                +--------------------------------+
```
 
### 2.5 `/movie/:id` — Movie detail
 
**The user comes here to:** rate a movie they watched, or mark it as watched so it stops appearing in recommendations.
 
**Calls:** `GET /api/v1/movies/:id`, `POST /api/v1/ratings`, `POST /api/v1/movies/:id/watch`
 
```
+----------------------------------------------------------+
|  <- Back to recommendations                              |
|                                                          |
|  HORROR                                                  |
|  The Shining                                             |
|  IMDb 8.4/10 · 1,248,440 votes                           |
|  View on IMDb                                            |
|                                                          |
|  Your rating (1–10)                                      |
|  [ Select a rating v ]   [ Save rating ]                 |
|                                                          |
|  [ Mark as watched ]                                     |
|                                                          |
|  Your rating has been saved.            <- status line   |
+----------------------------------------------------------+
 
Already rated:    the button reads [ Update rating ]
Already watched:  the button reads [ Already watched ] and is disabled
Loading:          "Loading movie..."
Error:            the message from section 3, with a link back to the list
```
 
Saving a rating also marks the movie as watched, so it does not come back in the next list.
 
---