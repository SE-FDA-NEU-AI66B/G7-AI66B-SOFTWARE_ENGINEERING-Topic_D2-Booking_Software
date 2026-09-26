# Traceability

Every screen traces back to a feature and forward to the issue that built it.
This table is the single source of truth for Milestone 1 section 6 and for the
Milestone 4 report. Keep it current - a PR that adds a route and does not
update this file should not be approved.

| Route | Purpose | Access | Priority | Feature | Story issue | PR | Status |
|---|---|---|---|---|---|---|---|
| `/` | Landing page | G | P0 | F1 | — | TBD | Not started |
| `/login` | Sign in / sign up | G | P0 | F1 | — | TBD | Not started |
| `/recommendations/setup` | Ask theme/topic and companion before generating list | U | P0 | F4 | #27, #28 | TBD | Not started |
| `/recommendations` | Show personalized or cold-start movie list | U | P0 | F2 | #23, #25, #29, #30, #31, #32 | TBD | Not started |
| `/movie/:id` | Movie detail — view info, mark as watched, rate | U | P0 | F3 | #24, #26 | TBD | Not started |
| `/profile/ratings` | View and manage movies you've rated | U | P1 | F3 | — | TBD | Not started |

**Access codes:** G = guest (not logged in) · U = authenticated user · A = admin

**Status:** Not started / In progress / Done

## Business rules

Numbered, so issues and tests can cite them.

| # | Rule | Enforced where | Tested by |
|---|---|---|---|
| BR1 | Don't recommend already-watched movies | /recommendations | TBD |
| BR2 | Don't recommend movies above user's age rating | /recommendations | TBD |
| BR3 | Max 10 movies per recommendation request | /recommendations | TBD |
| BR4 | Min 6.0/10 rating for personalized pool | /recommendations | TBD |
| BR5 | Personalized mode requires ≥5 rated/watched movies | /recommendations | TBD |
| BR6 | Cold-start uses trending/critically acclaimed movies | /recommendations | TBD |
| BR7 | No duplicate movies in one result list | /recommendations | TBD |
| BR8 | Min 100 ratings to qualify for cold-start pool | /recommendations | TBD |
| BR9 | Tie-break by rating count then release year | /recommendations | TBD |
