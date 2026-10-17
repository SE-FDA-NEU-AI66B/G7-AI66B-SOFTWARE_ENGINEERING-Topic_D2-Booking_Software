# MILESTONE 3 DOCUMENTATION: `docs/ui.md`

**Project:** Group 07 — SmartCine (Movie Recommendation System)

---

## SECTION 1: P0 User Stories & Status

### 1.1. Status Table

| Story | Title | Screen(s) | Route | API Endpoint(s) | Status | Issue |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **US10** | Select a profile before watching | Profiles | `/profiles` | `GET /api/profiles`, `POST /api/profiles/select` | works | `#10` |
| **US06** | Ask for theme/topic before recommending | Recommendation Setup | `/recommendations/setup` | `GET /api/categories`, `GET /api/themes` | works | `#06` |
| **US01** | Cold-start recommendations (<5 ratings) | Recommendations | `/recommendations` | `POST /api/recommendations` | works | `#01` |
| **US03** | Personalized romance-thriller recommendations | Recommendations | `/recommendations` | `POST /api/recommendations` | works | `#03` |
| **US04** | Exclude watched movies from recommendations | Movie Detail / Recs | `/movie/:id`, `/recommendations` | `POST /api/movies/:id/watched`, `POST /api/recommendations` | works | `#04` |
| **US02** | Rate a watched movie (Upsert) | Movie Detail | `/movie/:id` | `POST /api/movies/:id/rate`, `GET /api/movies/:id` | works | `#02` |

---

### 1.2. Screen Flow Diagram

```text
                         [ Start / Login ]
                                │
                                ▼
                     ┌──────────────────────┐
                     │      /profiles       │  (US10: Profile Selection)
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │/recommendations/setup│  (US06: Theme & Topic Selection)
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │   /recommendations   │  (US01: Cold-Start / US03: Personalized
                     └──────────┬───────────┘   US04: Exclude Watched / US07: Quality Filter)
                                │
                                ▼
                     ┌──────────────────────┐
                     │      /movie/:id      │  (US02: Rate Movie / Mark Watched)
                     └──────────────────────┘
```

---

## SECTION 2: Wireframes & Four-State UI

### 2.1. P0 Screens Summary & Wireframe Specs

#### Screen 1: Profile Selection (`/profiles`)

* **Purpose:** "The user comes here to select which profile is watching before getting recommendations, ensuring rating history and recommendations remain separate per person."
* **Calls:** `GET /api/profiles`, `POST /api/profiles/select`

![Profile selection screen](images/profiles.png)

```text
+-----------------------------------------------------------------------------------+
|  SmartCine                                                         [ Logout ]     |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|                                Who is watching?                                   |
|                                                                                   |
|           +-----------------------+       +-----------------------+               |
|           |       [Avatar 1]      |       |       [Avatar 2]      |               |
|           |                       |       |                       |               |
|           |         Duyen         |       |       Housemate       |               |
|           |     (20 ratings)      |       |      (3 ratings)      |               |
|           +-----------------------+       +-----------------------+               |
|                                                                                   |
|                              [ + Add New Profile ]                                |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

#### Screen 2: Recommendation Setup (`/recommendations/setup`)

* **Purpose:** "The user comes here to pick a theme, topic, or watch context (e.g., watching alone or with companions) before recommendations are generated."
* **Calls:** `GET /api/themes`, `GET /api/profiles`

```text
+-----------------------------------------------------------------------------------+
|  SmartCine  |  Active Profile: Duyen                                [ Switch ]    |
+-----------------------------------------------------------------------------------+
|  < Back to Profiles                                                               |
|                                                                                   |
|  1. Who are you watching with?                                                    |
|     (•) Just Me                                                                   |
|     ( ) With Companion -> [ Select Profile: Housemate v ]                         |
|                                                                                   |
|  2. What theme or topic do you want to watch tonight?                             |
|     [ Romance & Thriller ]  [ Horror & Suspense ]  [ Sci-Fi & Twist ]             |
|     [ Emotional Drama    ]  [ Mind-Bending      ]  [ Light Comedy   ]             |
|                                                                                   |
|  3. Max duration limit (Optional):                                                |
|     [ Under 90 mins v ]                                                           |
|                                                                                   |
|                         [ Get Recommendations -> ]                                |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

#### Screen 3: Movie Detail & Rating (`/movie/:id`)

* **Purpose:** "The user comes here to view movie details, submit or update a rating (1–10), and mark the movie as watched to exclude it from future recommendations."
* **Calls:** `GET /api/movies/:id`, `POST /api/movies/:id/rate`, `POST /api/movies/:id/watched`

```text
+-----------------------------------------------------------------------------------+
|  SmartCine  |  Active Profile: Duyen                                [ Switch ]    |
+-----------------------------------------------------------------------------------+
|  < Back to Recommendations                                                        |
|                                                                                   |
|  +--------------------+   The Invisible Guest (2016)                              |
|  |                    |   Genre: Thriller, Crime, Mystery | Runtime: 106m         |
|  |    [ Poster ]      |   Age Rating: 15+ | Overall Rating: 8.1/10 (12,400 ratings)|
|  |                    |                                                           |
|  |                    |   A successful entrepreneur accused of murder has 3 hours |
|  +--------------------+   to come up with an invincible defense...                |
|                                                                                   |
|  -------------------------------------------------------------------------------  |
|  YOUR ACTIVITY (Profile: Duyen)                                                   |
|                                                                                   |
|  Your Rating: [ ★ ★ ★ ★ ★ ★ ★ ★ ☆ ☆ ] (8/10)   [ Submit / Update Rating ]        |
|                                                                                   |
|  Watch Status: [ ✓ Marked as Watched ]  (Excludes from future recommendations)    |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

### 2.2. Four-State Wireframe (Screen: Recommendations — `/recommendations`)

* **Purpose:** "The user comes here to view their personalized or cold-start list of up to 10 recommended movies based on profile data and selected setup preferences."
* **Calls:** `POST /api/recommendations`, `GET /api/movies/re-watch-suggestion`

#### 1. Empty State (`/recommendations`)

```text
+-----------------------------------------------------------------------------------+
|  SmartCine  |  Active Profile: Duyen                                [ Switch ]    |
+-----------------------------------------------------------------------------------+
|  < Adjust Setup Criteria                                                          |
|                                                                                   |
|  Recommendations for "Horror" + "Under 90 mins"                                   |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                                                                             |  |
|  |                         🎬 No Movies Found                                  |  |
|  |                                                                             |  |
|  |   We couldn't find movies matching all your selected strict filters.        |  |
|  |   All matching movies may have already been marked as watched.              |  |
|  |                                                                             |  |
|  |                   [ Reset Filters / Change Topic ]                          |  |
|  |                                                                             |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

#### 2. Loading State (`/recommendations`)

```text
+-----------------------------------------------------------------------------------+
|  SmartCine  |  Active Profile: Duyen                                [ Switch ]    |
+-----------------------------------------------------------------------------------+
|  < Adjust Setup Criteria                                                          |
|                                                                                   |
|  Curating top choices for Duyen...                                                |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                                                                             |  |
|  |                        ( ◌ ) Analyzing preferences...                       |  |
|  |                  [=======================............] 65%                  |  |
|  |                                                                             |  |
|  |        Applying filters: Excluding 20 watched movies | Min Rating: 6.0      |  |
|  |                                                                             |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

#### 3. Error State (`/recommendations`)

```text
+-----------------------------------------------------------------------------------+
|  SmartCine  |  Active Profile: Duyen                                [ Switch ]    |
+-----------------------------------------------------------------------------------+
|  < Adjust Setup Criteria                                                          |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                                                                             |  |
|  |  Recommendation Engine Unavailable                                          |  |
|  |                                                                             |  |
|  |  We could not reach the recommendation service. Your session or profile     |  |
|  |  selection may have expired.                                                |  |
|  |                                                                             |  |
|  |  [ Try Again ]     [ Return to Profile Selection ]                          |  |
|  |                                                                             |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

#### 4. Data State (`/recommendations`)

```text
+-----------------------------------------------------------------------------------+
|  SmartCine  |  Active Profile: Duyen                                [ Switch ]    |
+-----------------------------------------------------------------------------------+
|  Recommended for You (Romance & Thriller)                         [ Refresh List ]|
|  Showing Top 10 Movies • Single Profile Mode                                      |
|  -------------------------------------------------------------------------------  |
|                                                                                   |
|  1. The Invisible Guest (2016)                    ★ 8.1/10 (12.4k ratings)        |
|     Plot: Complex murder mystery with unexpected twists.                          |
|     Tags: Thriller, Mystery | Match: 98%                                          |
|     [ View Details & Rate ]  [ Mark Watched ]                                     |
|  -------------------------------------------------------------------------------  |
|  2. Decision to Leave (2022)                      ★ 7.8/10 (5.1k ratings)         |
|     Plot: A detective falls for a mysterious widow in a murder investigation.     |
|     Tags: Romance, Thriller, Crime | Match: 94%                                   |
|     [ View Details & Rate ]  [ Mark Watched ]                                     |
|  -------------------------------------------------------------------------------  |
|  ... (Items 3 to 10 follow)                                                       |
|                                                                                   |
|  -------------------------------------------------------------------------------  |
|  [ IDLE SUGGESTION POPUP (Triggers after 30s idle) ]                              |
|  Can't decide? Re-watch your top favorite: "Ex Machina" (Your Rating: 9/10)       |
|  [ Watch Again ]  [ Dismiss ]                                                     |
+-----------------------------------------------------------------------------------+
```

---

## SECTION 3: Error Messages

| API Error Code | Business Rule | Exact User-Facing Message |
| :--- | :--- | :--- |
| `400 Bad Request` | BR1 | "This movie has already been marked as watched and cannot be added to your watch list." |
| `403 Forbidden` | BR2 | "This movie is rated above your profile's age limit rating setting." |
| `422 Unprocessable Entity` | BR3 | "Recommendation request exceeded the maximum limit of 10 movies per query." |
| `404 Not Found` | BR4 | "No movies met the minimum rating threshold of 6.0/10 for your selected theme." |
| `200 OK` (Fallback) | BR5 & BR6 | "You have rated fewer than 5 movies. Showing trending & critically acclaimed movies to get you started!" |
| `500 Internal Error` | BR7 | "Deduplication check failed while generating recommendation set. Please try again." |
| `400 Bad Request` | BR8 | "Cold-start recommendation pool contains movies with fewer than 100 ratings." |
| `400 Bad Request` | BR10 | "No active profile selected. Please select a profile before requesting recommendations." |

---

## SECTION 4: What Changed Since M2

### Architecture Change Summary

* **Added Endpoint:** `POST /api/profiles/select`
* **Added Database Column:** `profiles.age_rating_limit` (`INTEGER`, Default: `18`)
* **Modified Endpoint:** `POST /api/recommendations` now requires `profile_id` in the request header/body instead of relying solely on `account_id`.

### Why this change was made

During M2 API design, recommendations were implicitly scoped directly to the overall user account (`account_id`). When wireframing the `/profiles` and `/recommendations/setup` screens for Milestone 3, we realized that shared accounts (e.g., housemates or family members sharing one SmartCine account) would contaminate each other's rating history and recommendation outputs if scoping was only at the account level.

To satisfy BR10 and US10, we added explicit profile selection state handling (`POST /api/profiles/select`) and updated the recommendation API schema to accept `profile_id`. This guarantees complete data isolation between individual users on the same account.