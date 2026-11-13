# Operations

## 4. Known risks and technical debt

| Item | Layer | What could happen | Plan |
|---|---|---|---|
| SQLite is on Render's ephemeral filesystem | infrastructure | Ratings, watch history, and account changes disappear after restart, spin-down, or redeploy. | accepted — this is a free demo; user data is not promised to persist, and the reset behavior is documented. |
| Vote counts for movie IDs 31–42 are rounded | data | Trending order and vote totals differ from the IMDb snapshot. | accepted — the 42-title catalog is demo seed data; refresh values from the permitted source before broader use. |
| BR2 age filtering and BR9 release-year tie-break are not built | code | Recommendations may violate age preferences or resolve ties differently from the requirement. | accepted — the current schema and CSV lack age-rating and release-year fields; add them before claiming these rules are enforced. |
| Sign-in attempts are not rate-limited | code | Repeated password guesses can target the public login endpoint. | accepted — the account is a documented demo account, not a public account service; add throttling before inviting real users. |
| Free Render service sleeps after 15 minutes idle | infrastructure | The first visit after sleep can take about a minute. | accepted — the free plan suits this class demo; the delay is documented for visitors. |
| Frontend has no automated UI tests | tests | A screen-flow regression can pass lint and build. | accepted — current CI checks lint/build and the P0 API flows are tested; add browser tests before expanding the UI. |

## 5. Maintenance plan

| Area | What to do | Owner | How often |
|---|---|---|---|
| Bugs | Triage reports, reproduce, add a regression test, and fix through a reviewed PR. | @KatsuroHuy | Weekly and on each report |
| Dependencies | Review Python and npm updates; run tests, frontend lint, and build before merging. | @th3dummyking | Monthly |
| Data backups | Keep `data/movies.csv` as the reviewed, versioned source and verify `python init_db.py` rebuilds SQLite; runtime user data has no backup on the free plan. | @phuonglinhtla | Before each release |
| Monitoring | Check Render deploy events/logs and `/health`; investigate non-200 health checks or repeated request errors. | @Nvhwng | Weekly and after deploys |
| Documentation | Check setup, operations, data-reset notes, and test commands against the live service and code. | @phuonglinhtla | After each release |
| Regression checks | Run `python -m pytest -v` and `cd frontend && npm run lint && npm run build`. | @KatsuroHuy | Every PR |

## 6. Lessons learned

1. **A passing happy path did not ensure genre filtering worked in cold-start mode.** TC-33 exposed the US06 bug (#106); we fixed the query and kept the regression test. Next time, write acceptance tests for each mode and filter before implementation.
2. **Ten seed movies per genre were not enough when watched movies were excluded.** Expanding to 14 per genre (#100) made the exact-ten cold-start case testable. Next time, size fixtures for exclusions and boundary cases during backlog refinement.
3. **A local SQLite file is convenient but does not survive the free host's lifecycle.** We documented the reset behavior and seed-on-start command. Next time, decide persistence from user-data requirements before deployment and make the limitation visible before collecting data.
