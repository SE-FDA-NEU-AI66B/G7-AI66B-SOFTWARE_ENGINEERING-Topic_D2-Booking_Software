# Architecture
## Container

```
+-------------+    HTTPS     +----------------+   redirect    +------------------+
|    User     | -----------> |    Web App     | ------------> |  Streaming Site  |
| (phone/desk)| <----------- |    (React)     | watch_session | (mock in demo)   |
+-------------+ rendered UI  +----------------+      id       +------------------+
                                     |                                 |
                                     | REST/JSON                       | watch events
                                     | JWT + X-Profile-Id              | signed JSON (HMAC)
                                     v                                 |
                             +----------------+                        |
                             |  API (FastAPI) | <----------------------+
                             +----------------+
                                |           |
                          SQL   |           |  GET/SET lists
                                v           v
                        +------------+  +---------+
                        | PostgreSQL |  |  Redis  |
                        +------------+  +---------+

        +---------------+   CSV    +------------------+   bulk upsert   +------------+
        | Movie dataset | -------> | Catalog Importer | --------------> | PostgreSQL |
        +---------------+          +------------------+                 +------------+
```

> Mọi "Service" bên dưới là module Python trong **một** app FastAPI, gọi nhau bằng function call. Không có service nào deploy riêng.

> PostgreSQL và Redis là kiến trúc đích. Bản M2 (walking skeleton) chạy SQLite, xem ADR-1.

## Component (API)

```
   Web App                                   Streaming Site
      | REST/JSON                                   | signed event
      v                                             v
+---------------------+                 +----------------------+
| Auth middleware     |                 | Signature verifier   |
| JWT + X-Profile-Id  |                 | HMAC + timestamp     |
+---------------------+                 +----------------------+
      | account_id, profile_id                      | verified event
      v                                             v
+--------------------------------------------------------------+
| Routers: auth | profiles | recommendations | movies | callback|
+--------------------------------------------------------------+
   |            |               |                |           |
   | login      | profile CRUD  | profile ids,   | score /   | watch
   |            |               | theme          | watched   | event
   v            v               v                v           v
+--------+  +---------+  +----------------+  +--------+  +---------+
| Auth   |  | Profile |  | Recommendation |  | Rating |  | Watch   |
| Service|  | Service |  | Service        |  | Service|  | Service |
+--------+  +---------+  +----------------+  +--------+  +---------+
   |            |               |   |             |           |
   |            |               |   | get/set     |           |
   |            |               |   | list        | invalidate|
   |            |               |   v             v           v
   |            |               |  +--------------------------+
   |            |               |  |  Cache adapter  -> Redis |
   |            |               |  +--------------------------+
   |   SQL      |   SQL         |  SQL           SQL        SQL
   v            v               v                v           v
+--------------------------------------------------------------+
| Repositories (SQLAlchemy)  ------------------->  PostgreSQL  |
+--------------------------------------------------------------+
```

### Recommendation Service

```
 profile ids, theme
        |
        v
+--------------------+
| Signal counter     |  BR5
+--------------------+
    | < 5       | >= 5
    v           v
+-----------+  +----------------+
| Cold-start|  | Personalized   |
| BR6, BR8  |  | BR4            |
+-----------+  +----------------+
        \         /  candidates
         v       v
     +-----------------------+
     | Filter                |  BR1 watched, BR2 age, theme
     +-----------------------+
                |
                v
     +-----------------------+
     | Ranker                |  BR9
     +-----------------------+
                | top 10 per profile
                v
     +-----------------------+
     | Merger (2 profiles)   |  BR10, US05
     +-----------------------+
                | merged list
                v
     +-----------------------+
     | Assembler             |  BR7 unique, BR3 max 10
     +-----------------------+
```

# Data model

## ERD (core)

```
+------------------+ 1        1..* +--------------------+
| account          |---------------| profile            |
| PK id            |               | PK id              |
|    email         |               | FK account_id      |
|    password_hash |               |    display_name    |
+------------------+               |    max_age_rating  |
                                   +--------------------+
                                       | 1            | 1
                                       |              |
                                       | 0..*         | 0..*
                              +----------------+  +-------------------+
                              | rating         |  | watch_history     |
                              | PK id          |  | PK profile_id     |
                              | FK profile_id  |  | PK movie_id       |
                              | FK movie_id    |  |    source         |
                              |    score 1-10  |  |    first_watched  |
                              +----------------+  +-------------------+
                                       | 0..*         | 0..*
                                       |              |
                                       | 1            | 1
                                   +--------------------+ 1        0..* +-------------+
                                   | movie              |---------------| movie_genre |
                                   | PK id              |               | FK movie_id |
                                   |    title           |               | FK genre_id |
                                   |    release_year    |               +-------------+
                                   |    runtime_minutes |                      | 0..*
                                   |    age_rating      |                      |
                                   |    rating_count    |                      | 1
                                   |    avg_rating      |               +-------------+
                                   +--------------------+               | genre       |
                                                                        | PK id       |
                                                                        |    name     |
                                                                        +-------------+
```

## ERD (Streaming Site tracking)

```
+-----------------+ 1       0..* +--------------------+ 0..*       1 +-----------+
| profile         |--------------| watch_session      |--------------| movie     |
+-----------------+              | PK id              |              +-----------+
                                 | FK profile_id      |
                                 | FK movie_id        |
                                 |    partner         |
                                 |    status          |
                                 |    expires_at      |
                                 +--------------------+
                                           | 1
                                           |
                                           | 0..*
                                 +--------------------+
                                 | watch_event        |
                                 | PK id              |
                                 | FK watch_session_id|
                                 |    event_id        |
                                 |    event_type      |
                                 |    watched_seconds |
                                 |    runtime_seconds |
                                 +--------------------+
```

## Table description

| Table | Key / constraint |
|-------|------------------|
| account | `email` UNIQUE, `password_hash` NOT NULL |
| profile | FK `account_id` CASCADE · UNIQUE(`account_id`, `display_name`) · `max_age_rating` default 18 |
| movie | `rating_count` ≥ 0 · `avg_rating` generated from rating sum / count · `age_rating` ≥ 0 |
| genre, movie_genre | `name` UNIQUE · PK(`movie_id`, `genre_id`) |
| rating | `score` CHECK 1–10 · UNIQUE(`profile_id`, `movie_id`) → re-rate = upsert (US02) |
| watch_history | PK(`profile_id`, `movie_id`) · `source` IN (manual, partner_site) |
| watch_session | `id` random uuid, given to the Streaming Site · `status` IN (open, completed, expired) |
| watch_event | UNIQUE(`watch_session_id`, `event_id`) → duplicate callbacks ignored · `watched_seconds` ≤ `runtime_seconds` |

## Business rules

| BR | Data | Enforced by |
|----|------|-------------|
| BR1 | watch_history | Query: exclude rows in watch_history. Row written on manual mark, or on partner progress ≥ 90% |
| BR2 | movie.age_rating, profile.max_age_rating | Query: `age_rating <= max_age_rating` |
| BR3 | — | Code: `LIMIT 10` |
| BR4 | movie.avg_rating | Query: ≥ 6.0, personalized pool only |
| BR5 | rating + watch_history | Query: count distinct movies ≥ 5 |
| BR6 | movie | Code path when BR5 fails |
| BR7 | — | Code: dedupe in Assembler |
| BR8 | movie.rating_count | Query: ≥ 100, cold-start pool only |
| BR9 | movie.rating_count, release_year | `ORDER BY score, rating_count DESC, release_year DESC` |
| BR10 | profile.account_id · rating/watch_history keyed by profile_id | FK; service rejects companion from another account |

## User story → tables

| US | Tables |
|----|--------|
| US01 | movie, rating, watch_history |
| US02 | rating |
| US03 | rating, movie, movie_genre |
| US04 | watch_history, watch_session, watch_event |
| US05 | profile, rating |
| US06 | genre, movie_genre |
| US07 | movie |
| US08 | — (code) |
| US09 | rating, watch_history |
| US10 | account, profile |

# API design

#### Core RESTful APIs (P0 User Stories)

| Method | Path | Input | Success | Errors |
|---|---|---|---|---|
| **POST** | `/api/v1/auth/login` | `email`, `password` | **200** · `access_token` (JWT), list of profiles | **400** missing required credentials<br>**401** invalid email or password *(US01, US10)* |
| **GET** | `/api/v1/profiles` | *Header:* `Authorization: Bearer <access_token>` | **200** · list of profiles belonging to the account (`id`, `display_name`, `max_age_rating`) | **401** unauthorized account token *(US10)* |
| **POST** | `/api/v1/profiles/select` | *Header:* `Authorization: Bearer <access_token>`<br>`profile_id` | **200** · `active_profile_id`, `redirectTo: "/recommendations"` | **401** unauthorized account token<br>**404** profile not found or does not belong to account *(US10, BR10)* |
| **GET** | `/api/v1/recommendations/setup/genres` | *Header:* `Authorization: Bearer <access_token>`, `X-Profile-Id: <profile_id>` | **200** · list of available genres/themes (e.g., Action, Horror) | **401** missing or invalid JWT<br>**403** missing or invalid `X-Profile-Id` header *(US06)* |
| **GET** | `/api/v1/recommendations` | *Header:* `Authorization: Bearer <access_token>`, `X-Profile-Id: <profile_id>`<br>*Query:* `genre_id` *(optional)*, `companion_profile_id` *(optional — triggers the ratio-merge in US05; must belong to the same account as BR10 requires)* | **200** · list of 10 unique movies (personalized, cold-start, or merged if `companion_profile_id` is present) | **401** unauthorized JWT<br>**403** missing active profile header<br>**404** `companion_profile_id` not found or belongs to another account (BR10)<br>**422** invalid `genre_id` query parameter *(US01, US03, US05; BR1–BR10)* |
| **POST** | `/api/v1/ratings` | *Header:* `Authorization: Bearer <access_token>`, `X-Profile-Id: <profile_id>`<br>`movie_id`, `score` (1-10) | **201** · rating created or updated (upsert) | **400** score outside 1-10 range<br>**401** unauthorized<br>**404** movie_id not found *(US02)* |
| **POST** | `/api/v1/movies/:id/watch` | *Header:* `Authorization: Bearer <access_token>`, `X-Profile-Id: <profile_id>` | **200** · movie marked as watched manually in `watch_history` | **401** unauthorized<br>**404** movie ID not found in database *(US04, BR1)* |

#### Partner Callback API (External Streaming Integration)

| Method | Path | Input | Success | Errors |
|---|---|---|---|---|
| **POST** | `/api/v1/callback/watch-event` | *Header:* `X-Signature: <hmac_sha256>`<br>`watch_session_id`, `event_id`, `watched_seconds`, `runtime_seconds`<br>*(note: `profile_id` is not passed directly — it is resolved server-side from `watch_session_id` via the `watch_session` table)* | **200** · watch event recorded (written to `watch_history` if progress ≥ 90%) | **401** invalid HMAC signature or expired timestamp<br>**404** watch_session_id not found<br>**422** duplicate callback event_id ignored *(BR1)* |

# Walking skeleton

**Route:** `GET /recommendations` · **Table:** `movie` (12 rows seeded from `data/movies.csv`)

**How to know it worked:** `http://localhost:5000/recommendations` shows an HTML table listing 10 movies (title, genre, rating), read live from the SQLite database — not hardcoded in the route.

![Walking skeleton running](images/walking-skeleton.png)

**The query behind the page:**

```sql
SELECT id, title, genre, rating FROM movie ORDER BY id LIMIT 10;
```

No business rules (BR1–BR10) are applied yet at this stage — this route will be extended with filtering, personalization, and cold-start logic in Sprint 3/4, on top of this same working route.

# Design decisions

### ADR-1: SQLite instead of PostgreSQL/Redis for M2

**Options:** SQLite (single file, no setup) · PostgreSQL via Docker · PostgreSQL installed directly on the machine.

**Chose:** SQLite, with in-memory caching via a `Cache adapter`. The Container diagram above shows the target architecture; migration happens gradually from Sprint 3.

**Why:** The instructor clones and runs the project via SETUP.md in 15 minutes. PostgreSQL + Redis require Docker or separate installation plus connection strings — the most likely point of failure in that first step. Schema is written in SQLAlchemy without Postgres-specific types (`citext`, native `uuid`), so switching DB later is just a connection-string change; `PRAGMA foreign_keys=ON` makes SQLite enforce FK/CASCADE the same way Postgres does. The mock Streaming Site runs as a route in the same app (`/mock-partner`), so no second container is needed yet.

**What would change our mind:** Concurrent writes from multiple real users, or measuring `/recommendations` slower than our latency target without an out-of-process cache.

---

### ADR-2: One FastAPI app with internal modules, not microservices

**Options:** One FastAPI app with Services as internal modules (function calls) · Each domain (Auth, Profile, Recommendation, Rating, Watch) as a separate microservice communicating over the network.

**Chose:** Auth, Profile, Rating, Watch, and Recommendation as modules inside one process, under `app/<module>/`.

**Why:** A 4-person team, one semester, no current need to scale any part independently. No network hop between modules means simpler debugging and testing within a single process, while the module boundaries stay clean enough to split out later if needed.

**What would change our mind:** Model inference becoming heavy enough to need independent scaling or deployment — at that point, only the Recommendation Service would be split out.

---

### ADR-3: JWT for account identity + X-Profile-Id header for profile context

**Options:** Re-issue a new profile-scoped JWT every time the user switches profiles · Use one JWT for account authentication plus a custom `X-Profile-Id` header to scope each request to the active profile.

**Chose:** JWT for account identity, `X-Profile-Id` header for profile context.

**Why:** SmartCine's 1 Account–N Profiles model (BR10) needs a lightweight way to know which profile a request is for, without the server overhead of re-issuing tokens on every profile switch. This also keeps concerns separate: the JWT proves who the account is, the header scopes which profile's data is being read or written.

**What would change our mind:** Introducing per-profile security policies (e.g. a PIN check for a kids' profile on sensitive actions) — at that point, isolated per-profile session tokens would be worth revisiting.

---

### ADR-4: Inbound webhook instead of polling for partner watch events
**Options:** SmartCine periodically polls the partner's API for playback progress · The partner pushes real-time watch events to SmartCine via an inbound webhook (`POST /api/v1/callback/watch-event`), authenticated with an HMAC-SHA256 signature.

**Chose:** Inbound webhook with HMAC-SHA256 signature verification.

**Why:** BR1 requires `watch_history` to update automatically from partner playback data. A webhook delivers updates in real time without the resource cost of repeated polling, and the HMAC signature confirms the request really came from the partner and wasn't tampered with.

**What would change our mind:** Traffic spiking high enough that incoming webhook calls would need to be queued (e.g. via Kafka/RabbitMQ) before hitting the database, instead of being written directly.


# What changed since M1

# Changes Since M1

This section summarises what changed between Milestone 1 (M1) and Milestone 2 (M2), why each change was made, and which documents were updated. Changes come from instructor feedback on M1 and from our own follow-up design decisions.

| # | Change | Trigger | Affected artefacts |
|---|--------|---------|--------------------|
| 1 | New actor and use cases for automatic watch tracking | Instructor feedback | Use case diagram, API contract, mock service |
| 2 | US01 merged with the old US10 (cold-start) | Instructor feedback | User stories |
| 3 | Account + Profiles model (Netflix-style) replaces the "companion" concept | Instructor feedback that US05 was too hard to build | Screens, business rules, US05, traceability |
| 4 | New US10 (profile selection) | Consequence of change 3, keeps the story count at 10 | User stories, traceability |

---

## 1. Updated Use Case Diagram: External Streaming Site as a New Actor

### Problem in M1
The only way the system learned that a user had watched a movie was the user pressing "Mark as watched" (US04). This is fully manual and depends on the user's honesty and discipline. Because SmartCine only redirects users to an external site to watch, that external site is a more objective source: it knows exactly how long the user watched and whether they finished. In M1 this actor was missing.

### Change
We add a new **secondary (external) actor: External Streaming Site**. It sends watch-progress data back to SmartCine, which updates the user's watched history automatically. Manual "Mark as watched" stays as a fallback.

### Scope: design the architecture, mock the integration
Free streaming sites do not offer public APIs or partnerships, so a real integration is not realistic. What matters for this assignment is that the architecture and contract are designed correctly. We therefore:

1. **Design the contract as if the integration exists**: actor, use case and API endpoint.
2. **Build a mock** for the demo: a small fake endpoint that plays the role of the external site and sends a callback to SmartCine, which demonstrates that the architecture works end to end. No real site is called.

### Contract

The exact fields below are our proposed design and can be adjusted during implementation.

- **Use case:** *Receive watch-progress callback* (actor: External Streaming Site; includes *Update watched history*).
- **Endpoint:** `POST /api/v1/callback/watch-event` is called by the external site (or by the mock).
- **Authentication:** request must include header `X-Signature: <hmac_sha256>`. SmartCine verifies the signature before processing (ADR-4); invalid or expired signatures return `401`.
- **Payload (example):** `{ "watch_session_id": "...", "event_id": "...", "watched_seconds": 5400, "runtime_seconds": 7200 }`
- **Note:** `profile_id` is not sent directly — it is resolved server-side from `watch_session_id` via the `watch_session` table.
- **Behaviour:** if `watched_seconds / runtime_seconds` reaches the completion threshold (≥90%), the movie is added to that profile's watched history (`watch_history`), as if the user had pressed "Mark as watched" (BR1). Duplicate `event_id` values for the same session are ignored (`422`).
---

## 2. User Story Change: US01 Merged with the Old US10

The two cold-start stories are merged into a single story.

**US01 — Cold-start recommendations for new or low-data users** · P0 · 3 points · Screen: `/recommendations`

> As Duyen, I want to receive relevant movie recommendations even before I've rated enough movies, so that I get value from the app immediately.

**Acceptance criteria**
- Given a user has fewer than 5 rated or watched movies (0 included), when they request recommendations, then the system returns a trending/critically acclaimed list instead of a personalised one (BR5, BR6).
- Given the cold-start list is generated, when displayed, then it contains exactly 10 movies, each with at least 100 ratings (BR3, BR8).

The old US10 number is freed and reused by the new profile-selection story (section 4).

---

## 3. Account and Profiles Model (Replaces the "Companion" Concept)

### Problem in M1
The instructor pointed out that US05 (recommendations when watching with a companion) was very hard to implement as written. A guest companion with no data also made it impossible to merge by real rating counts.

### Change
We adopt a **Netflix-style model**: one **account** (email/password login) holds multiple **profiles** (family members or roommates). Each profile has its own rating history and preferences. This resolves both pieces of feedback at once:

- Authentication is real, at the account level.
- Each "companion" is a profile with separate data, not an anonymous guest, so US05 can still merge recommendations in proportion to real rating counts.

### 3.1 Screens and flow (`docs/requirements.md`, section 6)
Add one row to the screens table, directly after `/login`:

| Screen | Purpose | Role | Priority |
|--------|---------|------|----------|
| `/profiles` | Select which profile is watching (like "Who's watching?") | U | P0 |

Updated flow: `/login` → **`/profiles`** → `/recommendations/setup` → `/recommendations`

### 3.2 New business rule (`docs/requirements.md`, section 5, after BR9)

**BR10 — Account and Profiles**
One account may contain multiple profiles (e.g. family members or roommates). Each profile maintains its own independent rating history and preferences. Recommendations are always generated per profile.

*Worked example:* The "Duyen" account has 2 profiles, "Duyen" (20 rated movies) and "Housemate" (5 rated movies). Logging into the account does not select a profile; the user must pick a profile at `/profiles` before reaching recommendations.

### 3.3 Revised US05 (`docs/requirements.md`, section 4)

**US05 — Recommendations for watching with a companion profile** · P1 · 5 points · Screens: `/profiles`, `/recommendations/setup`

> As Duyen, I want to pick a second profile from my account when watching together, so that the recommendations reflect both our tastes.

**Acceptance criteria**
- Given Duyen's account has 2 profiles (Duyen: 20 rated movies, Housemate: 5 rated movies), when both profiles are selected for a joint session, then the system builds each profile's personalised top list independently, then merges them proportionally to rating count (20:5 = 4:1): 8 movies from Duyen's list and 2 from Housemate's list.
- Given a movie appears in both profiles' individual top lists, when merging, then it is deduplicated and placed ahead of movies unique to only one profile.
- Given only one profile is selected, when recommendations are generated, then the list uses only that profile's data (unchanged from single-profile behaviour).

### 3.4 Traceability (`docs/traceability.md`)
Add one row:

| Screen | Purpose | Role | Priority | Feature | Related | Test | Status |
|--------|---------|------|----------|---------|---------|------|--------|
| `/profiles` | Select which profile is watching | U | P0 | F1 | — | TBD | Not started |

---

## 4. New User Story: US10 — Select a Profile Before Watching

Added so the project still has 10 user stories after merging the two cold-start stories.

**US10 — Select a profile before watching** · P0 · 2 points · Screen: `/profiles`

> As a user, I want to select which profile is watching before getting recommendations, so that each person's recommendations and ratings stay separate from others sharing the same account.

**Acceptance criteria**
- Given an account has 2 profiles, when the user logs in, then they must select a profile at `/profiles` before reaching `/recommendations/setup`.
- Given a profile is selected, when recommendations are generated or rating history is viewed, then only that profile's own data is used, never mixed with another profile on the same account (BR10).

---

## Summary of Document Updates

| Document | Update |
|----------|--------|
| Use case diagram | Add actor *External Streaming Site* and use case *Receive watch-progress callback* |
| `docs/requirements.md` §4 | Merge US01 with old US10; rewrite US05; add new US10 |
| `docs/requirements.md` §5 | Add BR10 |
| `docs/requirements.md` §6 | Add `/profiles`; update flow diagram |
| `docs/traceability.md` | Add `/profiles` row |
| Implementation | Add `POST /api/watch-events` and a mock external-site service for the demo |