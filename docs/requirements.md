# Group 07 - Movie Recommendation System - Requirements

## 1. Product vision
SmartCine is an intelligent movie recommendation platform for film enthusiasts who struggle to decide what to watch next. Instead of making users browse through large catalogs themselves, SmartCine learns from their viewing history and ratings to provide personalized recommendations that increasingly match their tastes.

## 2. Personas

### 2.1. Persona 1

**Ngọc Duyên** - 19 - second-year student at Hanoi University of Science and Technology, living in a rented room.

**Description:** Duyen usually takes advantage of mealtimes or her free time to watch movies alone. Since she does not want to pay for movies, she mainly searches for movies on free movie-streaming websites and also frequently refers to online movie-review groups to discover new movies. She particularly enjoys movies that combine romance and thriller elements, especially those with complex plots and many unexpected “twists.” However, when there are too many choices and she does not know what to watch, Duyen often goes back to watching old movies that she has enjoyed before. She is also quite likely to stop watching a movie if its pace is slow and not engaging enough. Since she often watches movies during short periods of time, such as mealtimes, Duyen wants the system to provide suitable recommendations from the beginning, for example, by asking who she is watching the movie with.

**Desired recommendation feature:** Asking “Who are you watching this movie with?”

**Goal:** Make use of her mealtimes to watch movies and relax after a day of studying.

**Blocked by:** Too many choices and difficulty determining which movies are worth watching.

**In her words:** “There are so many movies to watch, but finding one I actually want to watch is the problem.”

**Technical skill:** Comfortable using smartphones, movie-streaming websites, social media, and online review groups. She primarily uses her phone when searching for and choosing movies.

**Interview notes:** Interviewed individually on 18 September 2026 at our rented room about her movie-watching habits, preferences, and difficulties when choosing movies.

### 2.2. Persona 2

**Thuy Trang** - 20 - third-year student at Hanoi University of Civil Engineering, living in a rented room.

**Description:** Trang usually takes advantage of mealtimes to watch movies alone, mainly searching for movies on free movie-streaming websites. She particularly enjoys horror or thriller movies with a sad and emotional tone. However, choosing a movie is not always that simple. When she cannot find a suitable movie, Trang often returns to movies she has watched before, sometimes turning to recommendations on TikTok. For Trang, the actors' appearance is a key factor in determining whether she continues watching a movie. She would like the system to ask about the topic or content she wants to watch beforehand to narrow down the choices. Normally, she takes only about two minutes to choose a movie, but when watching with her boyfriend or friends, the process can take considerably longer because she needs to consider the preferences of multiple people.

**Goal:** Quickly find a movie that matches her preferences and the preferences of the people she is watching with.

**Blocked by:** Difficulty choosing a movie when watching with her boyfriend or friends because their preferences may differ; she also needs to search through multiple sources before finding a suitable movie.

**In her words:** “Normally, I choose a movie very quickly, but when watching with others, I can never seem to decide what to watch.”

**Technical skill:** Familiar with smartphones and social media, especially TikTok. The interface should be visually clear, simple, and easy to use, particularly for first-time users.

**Interview notes:** Interviewed individually on 18 September 2026 at our rented room about her movie-watching habits, preferences, and difficulties when choosing movies.
## 3. Scenarios

## 4. User stories

### US01 — Recommendations without rating anything

**Priority:** P0  
**Points:** 3  
**Screen:** `/recommendations`

**As Duyen, I want to receive movie recommendations without rating anything first so that I get value from the app immediately.**

**Acceptance criteria:**
- Given Duyen has **0 ratings**, when she opens the recommendations page, then the system displays a trending/critically-acclaimed list *(BR6)*.
- Given the list loads, when displayed, then it contains exactly **10 movies** *(BR3)*.

**Tasks:**
- Build cold-start query (trending/critically acclaimed, top 10) - @KatsuroHuy
- Build `/recommendations` page UI for 0-rating state - @th3dummyking

- Tests: 0-rating user gets exactly 10 trending movies - @PhuongLinhtla

---

### US02 — Rate a watched movie

**Priority:** P0  
**Points:** 3  
**Screen:** `/movie/:id`

**As Trang, I want to rate a movie I've watched so that future recommendations match my taste in thrillers and horror.**

**Acceptance criteria:**
- Given a user has watched a movie, when they submit a rating between **1 and 10**, then the rating is saved and reflected in their profile.
- Given a user has already rated a movie once, when they try to rate it again, then the system **overwrites the previous rating instead of creating a duplicate**.

**Tasks:**
- Build rating submission endpoint (upsert, not duplicate) - @Nvhwng
- Build rating UI on `/movie/:id` - @th3dummyking
- Tests: re-rating overwrites previous rating - @PhuongLinhtla

---

### US03 — Personalized romance-thriller recommendations

**Priority:** P0  
**Points:** 5  
**Screen:** `/recommendations`

**As Duyen, I want to see a personalized list of romance-thriller movies with twist endings so that I can quickly find something worth watching during my meal.**

**Acceptance criteria:**
- Given Duyen has **≥5 rated movies** tagged romance or thriller, when she requests recommendations, then the system returns a personalized list weighted toward those genres *(BR5)*.
- Given the personalized list is generated, when displayed, then it contains **at most 10 movies** *(BR3)*.

**Tasks:**
- Build collaborative-filtering query weighted by genre tags - @th3dummyking
- Build `/recommendations` personalized list UI - @Nvhwng
- Tests: ≥5 ratings triggers personalized path, max 10 results - @KatsuroHuy

---

### US04 — Exclude watched movies

**Priority:** P0  
**Points:** 3  
**Screen:** `/movie/:id`

**As Duyen, I want already-watched movies excluded from my default recommendations so that I don't waste time re-discovering the same titles.**

**Acceptance criteria:**
- Given a user has watched **25 movies**, when recommendations are generated, then none of those 25 movies appear in the result *(BR1)*.
- Given a user marks a new movie as watched, when they request recommendations again, then that movie is **immediately excluded** from the next result set.

**Tasks:**
- Add watched-exclusion filter to recommendation query - @KatsuroHuy
- Wire "mark as watched" action to affect next query immediately - @Nvhwng
- Tests: 25 watched movies never reappear in results - @PhuongLinhtla

---

### US05 — Recommendations for watching with others

**Priority:** P1  
**Points:** 5  
**Screen:** `/recommendations/setup`

**As Trang, I want to specify who I'm watching with so that the system suggests movies that balance my preferences with theirs.**

**Acceptance criteria:**
- Given Trang selects "watching with a friend" and adds their profile, when recommendations are generated, then the list reflects **both users' rating histories**, not Trang's alone.
- Given Trang watches alone (no companion selected), when recommendations are generated, then the list uses **only her own data**.

**Tasks:**
- Build companion-selection UI on `/recommendations/setup` - @th3dummyking
- Build merged-preference query (2 users' histories) - @th3dummyking
- Tests: solo vs. companion mode produce different result sets - @PhuongLinhtla

---

### US06 — Ask for theme/topic before recommending

**Priority:** P0  
**Points:** 5  
**Screen:** `/recommendations/setup`

**As Trang, I want to be asked what theme or topic I want to watch before seeing suggestions so that I don't have to search through multiple sources myself.**

**Acceptance criteria:**
- Given Trang opens the recommendation flow, when the list-request screen loads, then she is prompted to pick a theme/topic **before** any movies are shown.
- Given Trang selects **"horror"**, when recommendations are generated, then all **10 results are tagged horror** *(BR3, BR4)*.

**Tasks:**
- Build theme/topic picker UI on `/recommendations/setup` - @KatsuroHuy
- Wire theme filter into recommendation query - @th3dummyking
- Tests: selecting "horror" returns only horror-tagged results - @Nvhwng

---

### US07 — Filter out low-quality movies

**Priority:** P1  
**Points:** 3  
**Screen:** `/recommendations`

**As Duyen, I want low-quality/low-rated movies filtered out of my personalized list so that I don't stop halfway through a slow, disappointing movie.**

**Acceptance criteria:**
- Given a movie has a rating of **5.8/10**, when personalized recommendations are generated, then that movie is excluded *(BR4)*.
- Given a movie has a rating of **7.2/10**, when personalized recommendations are generated, then that movie is eligible for inclusion.

**Tasks:**
- Add rating-threshold filter to personalized query - @th3dummyking
- Tests: 5.8 excluded, 7.2 included - @PhuongLinhtla
- Update `docs/traceability.md` status for BR4 - @KatsuroHuy

---

### US08 — No duplicate movies in a list

**Priority:** P1  
**Points:** 2  
**Screen:** `/recommendations`

**As a user, I want each movie to appear only once per recommendation list so that the list doesn't feel repetitive or broken.**

**Acceptance criteria:**
- Given a recommendation list of **10 movies** is generated, when the list is returned, then all 10 movie IDs are **unique** *(BR7)*.
- Given a movie qualifies under multiple recommendation logics, when the final list is assembled, then it appears **only once**.

**Tasks:**
- Add de-duplication step to final result assembly - @th3dummyking
- Tests: no repeated movie ID across a 10-item list - @Nvhwng
- Update `docs/traceability.md` status for BR7 - @KatsuroHuy

---

### US09 — Re-watch suggestion when undecided

**Priority:** P2  
**Points:** 2  
**Screen:** `/recommendations`

**As Duyen, I want the option to re-watch a suggested old favorite when I can't decide so that I still have something to watch during my meal.**

**Acceptance criteria:**
- Given Duyen has been idle on the recommendation screen for **30 seconds** without selecting a movie, when the timeout triggers, then the system suggests one previously-watched movie she rated **≥8/10** *(BR9)*.
- Given no previously-watched movie meets the ≥8/10 threshold, when the timeout triggers, then the system **does not force** a re-watch suggestion.

**Tasks:**
- Build idle-timeout detection (30s) on `/recommendations` - @th3dummyking
- Build re-watch suggestion query (rated ≥8/10) - @Nvhwng
- Tests: no suggestion when no movie meets threshold - @PhuongLinhtla

---

### US10 — Cold-start recommendations for low-data users

**Priority:** P0  
**Points:** 5  
**Screen:** `/recommendations`

**As a user with very few ratings, I want to see trending/critically acclaimed movies instead of a poor personalized guess so that I still get a useful list early on.**

**Acceptance criteria:**
- Given a user has rated only **3 movies**, when they request recommendations, then the system returns the cold-start list, not a personalized one *(BR5/BR6)*.
- Given a cold-start movie is selected, when checked against BR8, then it must have **at least 100 ratings** to qualify for that pool.

**Tasks:**
- Build <5-ratings detection + cold-start fallback trigger - @th3dummyking
- Add min-100-ratings filter for cold-start pool - @KatsuroHuy
- Tests: 3-rating user gets cold-start list, not personalized - @Nvhwng

## 5. Business rules
### BR1 — Watched Movies
The system must not recommend movies the user has marked as watched or has watched at least 90% of the runtime.

**Worked example:**
If a user has watched 25 movies (marked watched or ≥90% runtime viewed), those 25 movies must be excluded from the recommendation results.

### BR2 — Age Rating Limit
The system must not recommend movies whose age rating is strictly higher than the user's allowed rating. A movie rated exactly at the user's allowed level is permitted.

**Worked example:**
If a user's allowed rating is 15, movies rated 18+ must not appear in their recommendations. A movie rated exactly 15 is allowed to appear.

### BR3 — Maximum Recommendations
Each recommendation request must return a maximum of 10 movies.

**Worked example:**
If the recommendation engine finds 18 suitable movies, SmartCine must display only the top 10 recommendations.

### BR4 — Minimum Movie Rating
A movie must have a minimum rating of 6.0/10 to be included in personalized recommendations. This threshold applies to the personalized (collaborative-filtering) pool only; the cold-start pool is governed separately by BR8.

**Worked example:**
If a movie has a rating of 5.8/10, it must be excluded from the personalized pool. A movie rated 7.2/10 can be recommended.

### BR5 — Preference Data Threshold
Personalized recommendations require at least 5 rated or watched movies as preference data. Users below this threshold fall under BR6 (Cold-Start Recommendations) instead.

**Worked example:**
If a user has rated only 3 movies, SmartCine must not generate a fully personalized list and must use the cold-start rules (BR6) instead.

### BR6 — Cold-Start Recommendations
New users below the BR5 threshold (fewer than 5 ratings) must receive recommendations based on trending or critically acclaimed movies rather than personalized preference data.

**Worked example:**
If a new user has rated 2 movies, SmartCine must use trending or critically acclaimed movies (see BR8 for eligibility) instead of personalized collaborative filtering.

### BR7 — Unique Recommendations
A movie must not appear more than once in the same recommendation result.

**Worked example:**
If the system generates 10 recommendations, all 10 movie IDs must be unique. The same movie cannot appear at positions 3 and 8.

### BR8 — Minimum Rating Count
A movie must have at least 100 ratings to qualify for the critically acclaimed / cold-start recommendation pool (see BR6).

**Worked example:**
If Movie A has 85 ratings with an average score of 8.9/10, it must be excluded. Movie B with 500 ratings and an average score of 8.4/10 qualifies.

### BR9 — Ranking Tie-Break
When multiple movies have an identical predicted score, they must be ordered by rating count (descending), then by release year (newest first).

**Worked example:**
Movie A and Movie B both score 8.5 predicted match. Movie A has 1,200 ratings, Movie B has 900. Movie A appears first.
## 6. Screens and flow



| Route | Purpose | Access | Priority |
|---|---|---|---|
| `/` | Landing page — intro, entry point | G | P0 |
| `/login` | Sign in / sign up | G | P0 |
| `/recommendations/setup` | Ask theme/topic and who you're watching with, before generating a list | U | P0 |
| `/recommendations` | Show personalized or cold-start movie list | U | P0 |
| `/movie/:id` | Movie detail — view info, mark as watched, submit a rating | U | P0 |
| `/profile/ratings` | View and manage movies you've rated | U | P1 |


**Flow diagram:**




```
                     +------------------+
                     |        /         |   (not signed in)
                     +------------------+
                              |
                              | sign in
                              v
                     +------------------+
                     |     /login       |
                     +------------------+
                              |
                              | success
                              v
               +-------------------------------+
               |   /recommendations/setup      |
               +-------------------------------+
                              |
                              | submit
                              v
   +-->  +--------------------------+   pick a movie    +------------------------+
   |     |     /recommendations     | -----------------> |      /movie/:id        |
   |     |                          | <----------------- |  rate / mark watched   |
   |     +--------------------------+        back        +------------------------+
   |                    |
   |                    | view ratings
   |                    v
   |          +------------------------+
   |          |    /profile/ratings    |
   |          +------------------------+
   |                    |
   +--------------------+
            back
```
