# Traceability

Every screen traces back to a feature and forward to the issue that built it.
This table is the single source of truth for Milestone 1 section 6 and for the
Milestone 4 report. Keep it current - a PR that adds a route and does not
update this file should not be approved.

| Route | Purpose | Access | Priority | Feature | Story issue | PR | Status |
|---|---|---|---|---|---|---|---|
| `/` | Landing page | G | P0 | F1 | — | TBD | Not started |
| `/login` | Sign in with email and password | G | P0 | F1 | — | # | In progress |
| `/recommendations/setup` | Ask theme/topic and companion before generating list | U | P0 | F4 | #27, #28 | TBD | Not started |
| `/recommendations` | Show personalized or cold-start movie list | U | P0 | F2 | #23, #25, #29, #30, #31, #32 | TBD | Not started |
| `/movie/:id` | Movie detail — view info, mark as watched, rate | U | P0 | F3 | #24, #26 | TBD | Not started |
| `/profile/ratings` | View and manage movies you've rated | U | P1 | F3 | — | TBD | Not started |
| `/profiles` | Select which profile is watching | U | P0 | F1 | #32 | #91 | In progress |

**Access codes:** G = guest (not logged in) · U = authenticated user · A = admin

**Status:** Not started / In progress / Done

## Business rules

Numbered, so issues and tests can cite them.

| # | Rule | Enforced where | Tested by |
|---|---|---|---|
| BR1 | Don't recommend already-watched movies | /recommendations | TBD |
| BR2 | Don't recommend movies above user's age rating | /recommendations | TBD |
| BR3 | Max 10 movies per recommendation request | /recommendations | test_recommendations_are_limited_to_10
| BR4 | Min 6.0/10 rating for personalized pool | /recommendations | test_recommendations_exclude_movies_rated_below_6 |
| BR5 | Personalized mode requires ≥5 rated/watched movies | /recommendations | test_fewer_than_five_preferences_gets_ten_cold_start_movies, test_five_preferences_uses_personalized_path |
| BR6 | Cold-start uses trending/critically acclaimed movies | /recommendations | test_recommendations_without_genre_returns_cold_start_list, test_cold_start_is_sorted_by_rating_then_vote_count |
| BR7 | No duplicate movies in one result list | /recommendations | TBD |
| BR8 | Min 100 ratings to qualify for cold-start pool | /recommendations | test_cold_start_excludes_movie_with_fewer_than_100_ratings, test_cold_start_includes_movie_with_exactly_100_ratings |
| BR9 | Tie-break by rating count then release year | /recommendations | TBD |
| BR10 | A profile belongs to exactly one account; a joint session can only merge profiles from the same account | /profiles, `get_current_profile` in `auth.py` | ...