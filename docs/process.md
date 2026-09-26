# Software Process — Recommendation System (Movies / Books / Courses)

## Section 1 — Chosen Process and Its Position on the Plan-driven ↔ Agile Spectrum

### (a) Model
Our team adopts a **Hybrid Incremental-Scrum Model**. Each cycle is a two-week Sprint consisting of five activities:

1. **Sprint Planning (2 hours):** The whole team selects items from the Product Backlog, prioritizing by the nearest milestone.
2. **Development (8–9 days):** Parallel work based on the following assignment:
   - **Nguyen Quang Huy (AI Engineer):** Experiments with recommendation algorithms (Collaborative Filtering, Content-Based, Hybrid), handles the cold-start problem, and evaluates offline metrics (Precision@K, NDCG).
   - **Be Thanh Dat (Backend Engineer):** Builds the user-specific recommendation API, designs the rating/item schema, implements caching (Redis), and integrates model serving.
   - **Hoang Thi Phuong Linh (Frontend Engineer):** Develops the recommendation UI, collects implicit feedback (clicks, dwell time), and connects to the backend API.
   - **Nguyen Vinh Hung (DevOps / QA Engineer):** Sets up CI/CD, writes unit and integration tests, monitors API latency, and ensures the fallback mechanism remains stable.
3. **Daily Standup (15 minutes):** Sync progress and surface blockers (e.g., model inference too slow, API timeouts).
4. **Sprint Review (1 hour):** Demo the increment to the instructor / beta users and gather feedback on real-world recommendation quality.
5. **Sprint Retrospective (30 minutes):** Inspect and adapt the process for the next Sprint.

**At the end of one cycle,** the team delivers a **Potentially Shippable Increment**—for example, a complete `/recommendations?user_id=` endpoint with a new algorithm, a genre-based recommendation feature, or a cold-start fallback (popularity-based) integrated into production.

### (b) Position
We position our process at **75% Agile — 25% Plan-driven**.

- **Plan-driven (25% — fixed for the whole semester):** The 4 milestones and the final demo date are immutable. This document, the final report, and repository access rules (public or instructor added as collaborator) are mandated by the course.
- **Agile (75% — adjustable each cycle):** We may pivot the recommendation algorithm between Sprints (e.g., from Matrix Factorization to a Two-Tower Neural Network if cold-start performance is poor). The order of feature development (movies first vs. books first) and UI design can change based on feedback.

## Section 2 — Five Diagnostic Questions

### 1. Are our requirements stable or volatile?
**Volatile.** An AI recommendation project is highly experimental. We may initially choose Collaborative Filtering, but only during implementation discover severe cold-start issues for new users and be forced to switch to a hybrid model. The API response format may also change when the frontend needs additional fields such as `confidence_score` or `explanation`. The number of content sources (movies, books, courses) may expand or shrink depending on our crawling capacity in the first Sprint.

### 2. Does the project have safety or legal impact?
**Low-to-moderate legal impact; no safety-critical concerns.** This is not a medical or aviation system. However, because we store user viewing history and ratings, we must respect privacy regulations (anonymize user IDs, avoid exposing personal data). We need documentation for milestones but do not require a rigid Change Control Board as in safety-critical projects.

### 3. Is the team large and distributed or small and co-located?
**Small (4 people) and co-located / hybrid.** All members attend the same university and can meet in person or online via Discord / Google Meet. Communication cost is low; no heavy process or multiple management layers are needed. A 15-minute daily standup is sufficient for synchronization. Roles are clearly split (AI, Backend, Frontend, DevOps/QA) but members can flexibly support each other.

### 4. Can the customer participate continuously?
**Hybrid availability.** The instructor acts as the primary customer and is only available at milestone checkpoints (plan-driven gates). However, we can continuously collect feedback from beta users (friends, other students) during each Sprint Review to evaluate real-world recommendation quality. Therefore, we need both formality with the instructor and agility to iterate based on actual user feedback.

### 5. What do organizational culture and contract constraints allow?
The course mandates **4 fixed milestones** and a **fixed final demo date**—these are plan-driven constraints we cannot change. The repository must be public or grant the instructor collaborator access. Beyond that, the team has full flexibility in: (a) tech stack choice (Python/FastAPI, React, PostgreSQL, Redis), (b) recommendation algorithms to experiment with each Sprint, and (c) internal task allocation.

## Section 3 — Critical Thinking: Risk of Choosing the Opposite Approach

If our team switched to a **Fully Plan-driven (Waterfall)** approach:
- **Biggest risk:** Architectural misalignment of the recommendation algorithm due to lack of early experimentation.
- **Mechanism of harm:** In Waterfall, we must select the algorithm (e.g., Pure Collaborative Filtering) during the Design phase and freeze it. By the Testing phase, we would discover the model completely fails for cold-start users (new users with no history receive random recommendations). Because there is no time to return to the Design phase, the team must either accept poor quality or drop the feature.
- **First observable symptom:** At the mid-term milestone (after 6–8 weeks), the `/recommendations` endpoint returns irrelevant results for a newly created demo account, but the team cannot pivot to a hybrid model because the Software Design Document was already approved and does not permit changes to the core architecture.

## Section 4 — Process Rules the Team Commits To

1. **"Every change reaches main through a Pull Request reviewed by at least one other member and passing CI (lint + unit test)."**  
   All code changes (backend, frontend, model notebooks) must go through a PR, be reviewed by at least one other member, and pass CI before merge.

2. **"Sprint length is two weeks; the backlog is re-prioritized at the start of each sprint based on the nearest milestone."**  
   Each Sprint lasts two weeks; the backlog is re-prioritized at Sprint Planning, favoring items that serve the upcoming milestone.

3. **"Any model with offline metric drop &gt;5% in Precision@10 or NDCG blocks deployment until root cause is documented in docs/model-log.md."**  
   If a new model drops offline performance by more than 5% compared to the baseline, deployment to the production API is blocked; the root cause must be recorded in `docs/model-log.md`.

4. **"All API changes must be documented in docs/api.md and include a Postman collection test before PR approval."**  
   Any API change (endpoint, request/response format) must update the documentation and include a Postman test collection before the PR can be approved.

5. **"Cold-start fallback (popularity-based or genre-based) must remain active in production even during primary model redeployment."**  
   The fallback mechanism for new users/items must always be active in production, even while deploying a new primary model, to ensure the API never returns errors or empty results.