# Traceability

Every screen traces back to a feature and forward to the issue that built it.
This table is the single source of truth for Milestone 1 section 6 and for the
Milestone 4 report. Keep it current - a PR that adds a route and does not
update this file should not be approved.

| Route | Purpose | Access | Priority | Feature | Story issue | PR | Status |
|---|---|---|---|---|---|---|---|
| `/` | Landing page | G | P0 | F1 | — | TBD | Not started |
| `/login` | Sign in with email and password | G | P0 | F1 | — | #91 | Done |
| `/recommendations/setup` | Ask theme/topic and companion before generating list | U | P0 | F4 | #27, #28 | #91 | Done |
| `/recommendations` | Show personalized or cold-start movie list | U | P0 | F2 | #23, #25, #29, #30, #31, #32 | TBD | Done |
| `/movie/:id` | Movie detail — view info, mark as watched, rate | U | P0 | F3 | #24, #26 | TBD | Done |
| `/profile/ratings` | View and manage movies you've rated | U | P1 | F3 | — | TBD | Not started |
| `/profiles` | Select which profile is watching | U | P0 | F1 | #32 | #91 | Done |

**Access codes:** G = guest (not logged in) · U = authenticated user · A = admin

**Status:** Not started / In progress / Done

## Business rules

Numbered, so issues and tests can cite them.

| # | Rule | Enforced where | Tested by |
|---|---|---|---|
| BR1 | Don't recommend already-watched movies | /recommendations | test_tc21_marking_movie_watched_removes_it_from_next_recommendations, test_tc22_rating_a_movie_also_marks_it_watched_so_it_is_not_recommended, test_tc23_boundary_25_watched_movies_never_reappear |
| BR2 | Don't recommend movies above user's age rating | /recommendations | TBD |
| BR3 | Max 10 movies per recommendation request | /recommendations | test_tc14_more_than_ten_qualifying_movies_returns_exactly_ten, test_tc07_zero_preferences_returns_ten_qualified_cold_start_movies |
| BR4 | Min 6.0/10 rating for personalized pool | /recommendations | test_tc15_personalized_rating_boundary_excludes_5_9_and_keeps_6_0 |
| BR5 | Personalized mode requires ≥5 rated/watched movies | /recommendations | test_tc08_four_preferences_still_uses_cold_start, test_tc12_exactly_five_preferences_uses_personalized_path |
| BR6 | Cold-start uses trending/critically acclaimed movies | /recommendations | test_tc07_zero_preferences_returns_ten_qualified_cold_start_movies, test_cold_start_is_sorted_by_rating_then_vote_count |
| BR7 | No duplicate movies in one result list | /recommendations | TBD |
| BR8 | Min 100 ratings to qualify for cold-start pool | /recommendations | test_tc09_movie_with_99_votes_is_excluded_from_cold_start, test_tc10_movie_with_exactly_100_votes_is_in_cold_start, test_tc27_every_movie_has_at_least_100_votes |
| BR9 | Tie-break by rating count then release year | /recommendations | TBD |
| BR10 | A profile belongs to exactly one account; a joint session can only merge profiles from the same account | /profiles, `get_current_profile` in `auth.py` | test_tc03_selecting_a_profile_of_another_account_returns_404, test_tc06_one_profiles_ratings_do_not_change_another_profiles_list |