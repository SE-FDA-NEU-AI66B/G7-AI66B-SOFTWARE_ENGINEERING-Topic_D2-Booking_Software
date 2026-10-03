# Architecture

Owner: Hưng (@Nvhwng)

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

## ADR

### ADR-1: M2 dùng SQLite, không dùng PostgreSQL/Redis

- **Context:** Giảng viên clone và chạy theo SETUP.md trong 15 phút. Postgres + Redis đòi Docker hoặc cài riêng, kèm connection string, và là điểm dễ hỏng nhất trong bước đầu.
- **Decision:** Walking skeleton (M2) dùng **SQLite** (một file, không cài thêm) và cache trong bộ nhớ qua `Cache adapter`. Sơ đồ Container ở trên là kiến trúc đích, migrate dần từ Sprint 3.
- **Consequences:**
  - SETUP.md chỉ cần `pip install` + một lệnh chạy.
  - Schema viết bằng SQLAlchemy, không dùng kiểu riêng của Postgres (`citext`, `uuid` gốc), nên đổi DB chỉ là đổi connection string. Bật `PRAGMA foreign_keys=ON` để FK và CASCADE chạy giống Postgres.
  - Cache adapter là điểm duy nhất biết về cache, nên thay dict bằng Redis không đụng tới Service.
- Mock Streaming Site chạy như một route trong cùng app (`/mock-partner`), không cần container thứ hai.
  - Thứ phải test lại khi migrate: ghi đồng thời và cột `avg_rating` generated.
- **What would change our mind:** Cần ghi đồng thời từ nhiều người dùng, hoặc đo được endpoint `/recommendations` chậm hơn mục tiêu latency khi không có cache ngoài tiến trình.

**Options:** SQLite (file, không cài thêm) · PostgreSQL + Docker · PostgreSQL cài trực tiếp trên máy
### ADR-2: Một app FastAPI, các Service là module

- **Context:** Nhóm 4 người, một học kỳ, chưa có nhu cầu scale từng phần riêng.
- **Decision:** Auth, Profile, Rating, Watch, Recommendation là module trong cùng một process. Ranh giới là function call và package `app/<module>/`.
- **Consequences:** Không có network hop, debug và test trong một process. Ranh giới module vẫn rõ để tách sau.
- **What would change our mind:** Model inference nặng đến mức cần scale hoặc deploy riêng, khi đó chỉ Recommendation Service tách ra.
**Options:** Một app FastAPI với module nội bộ · Tách mỗi domain thành microservice riêng

# Data model

Owner: Hưng (@Nvhwng)

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