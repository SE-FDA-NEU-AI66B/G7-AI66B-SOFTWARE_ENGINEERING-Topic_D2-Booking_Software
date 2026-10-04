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


# Architectural Decision Records 

### ADR-01: Authentication & User Profile Context Strategy

* **Context & Problem Statement:**
  The SmartCine system supports a **1 Account – N Profiles** domain model (one account contains multiple viewer profiles). The system requires a secure and lightweight mechanism to authenticate account identity while accurately preserving the active Profile context across all API requests (for recommendations, ratings, and watch history tracking).

* **Options Considered:**
  * **Option A:** Re-issuing a new profile-scoped JWT token every time the user switches profiles.
  * **Option B:** Utilizing a JWT token for Account Authentication alongside a custom `X-Profile-Id` HTTP Header for Profile Context.

* **Decision & Rationale:**
  * **Selected Option: Option B.**
  * **Rationale:**
    * Eliminates server overhead caused by frequent token re-issuance whenever users switch profiles.
    * Enforces a clear Separation of Concerns: JWT handles Account Identity, while the `X-Profile-Id` header explicitly scopes data operations to the target profile.

* **Conditions for Change:**
  * If granular security policies between profiles are introduced in the future (e.g., Kids profiles requiring a dedicated PIN verification per sensitive operation) $\rightarrow$ Re-evaluate issuing isolated per-profile session tokens.

---

### ADR-02: HTTP Status Code & Error Handling Standardization

* **Context & Problem Statement:**
  To maintain strict RESTful compliance and avoid the anti-pattern of "Always 200 OK" (returning status 200 even when error payloads exist in the body), the API architecture requires a standardized set of HTTP status codes across all endpoints.

* **Options Considered:**
  * **Option A:** Returning `200 OK` for all successful and failed requests, wrapping error details inside the JSON response body.
  * **Option B:** Standardizing a clean status code matrix: `200 OK` and `201 Created` for success; strictly utilizing `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, and `422 Unprocessable Entity` for error handling.

* **Decision & Rationale:**
  * **Selected Option: Option B.**
  * **Rationale:**
    * Satisfies academic and industry requirements for RESTful maturity and compliance.
    * Enables front-end clients to handle error states automatically via native HTTP response status codes without parsing JSON bodies first.
    * Clearly delineates syntax errors (`400`), authentication/permission failures (`401/403`), missing resources (`404`), and business/validation constraint violations (`422`).

* **Conditions for Change:**
  * If the platform expands to handle heavy asynchronous background processes (e.g., batch data export or video encoding) $\rightarrow$ Incorporate `202 Accepted`.

---

### ADR-03: External Streaming Partner Integration via Webhook

* **Context & Problem Statement:**
  In accordance with Business Rule BR1, SmartCine must automatically record playback progress into `watch_history` whenever users watch movies on external partner streaming sites. The integration method must be real-time, secure, and non-blocking.

* **Options Considered:**
  * **Option A:** SmartCine periodically polls the partner’s API to fetch playback progress (Polling mechanism).
  * **Option B:** The partner streams real-time watch events to SmartCine via an inbound Webhook (`POST /api/v1/callback/watch-event`) authenticated with an HMAC-SHA256 signature.

* **Decision & Rationale:**
  * **Selected Option: Option B.**
  * **Rationale:**
    * An event-driven webhook architecture delivers real-time updates while avoiding resource-heavy polling overhead on SmartCine servers.
    * Incorporating an HMAC-SHA256 signature in the request headers guarantees payload integrity and authenticates that requests originate from legitimate partners.

* **Conditions for Change:**
  * If high-volume streaming traffic creates extreme event spikes $\rightarrow$ Ingest incoming webhook payloads directly into a Message Queue (e.g., Apache Kafka / RabbitMQ) prior to database persistence.


---

### ADR-04: API Pagination Strategy for High-Volume Resource Collections

* **Context & Problem Statement:**
  Endpoints retrieving movie catalogs (`GET /api/v1/movies`), search results, and movie reviews are expected to handle large datasets. Delivering unpaginated datasets causes severe network latency and database overhead. The platform requires a standardized pagination strategy for collection resources.

* **Options Considered:**
  * **Option A:** Offset-based Pagination (`page` and `limit` query parameters).
  * **Option B:** Cursor-based / Keyset Pagination (`starting_after` or `cursor` token).

* **Decision & Rationale:**
  * **Selected Option: Option A (Offset-based Pagination).**
  * **Rationale:**
    * Offset-based pagination (`page` & `limit`) provides intuitive UI navigation (direct page jumping) for end-users browsing movie catalogs.
    * Simplifies client-side integration while remaining fully compatible with the project's relational database schema (`OFFSET` and `LIMIT` queries).

* **Conditions for Change:**
  * If movie catalog datasets or review feeds scale to millions of records causing SQL `OFFSET` performance degradation $\rightarrow$ Migrate high-traffic endpoints to Cursor-based Pagination.

---

### ADR-05: Standardized Error Response Payload Structure (RFC 7807)

* **Context & Problem Statement:**
  When API requests fail (e.g., validation errors `422` or authorization failures `403`), front-end clients require a predictable, machine-readable JSON error structure to display user-friendly error messages without breaking UI state.

* **Options Considered:**
  * **Option A:** Returning plain-text error messages or unstructured key-value JSON objects.
  * **Option B:** Adopting an RFC 7807-compliant JSON error structure featuring standard fields: `code`, `message`, `details` (field-level validation errors), and `timestamp`.

* **Decision & Rationale:**
  * **Selected Option: Option B.**
  * **Rationale:**
    * Establishes a uniform error format across all Microservices and Endpoints.
    * Allows front-end forms to map validation errors (`details` array) directly to specific input fields automatically.

* **Conditions for Change:**
  * If third-party integrations require custom error serialization schemas $\rightarrow$ Introduce explicit API versioning or header-based content negotiation for error payloads.