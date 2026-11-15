# Sprint log

One section per sprint. Fill it in **during** the sprint, not the night before
the milestone deadline - the commit timestamps on this file are part of the
evidence that the process was real.

## All sprints at a glance

| Sprint | Weeks | Scrum Master | Goal | Committed | Completed | Velocity |
|--------|-------|--------------|------|-----------|-----------|----------|
| 1 | 5–6 | @KatsuroHuy | Agree on vision, personas, scenarios, business rules and screens so all 10 user stories are clear and testable | 0 | 0 | n/a (requirements sprint) |
| 2 | 7–8 | @th3dummyking | Architecture, data model, API design and ADRs documented; walking skeleton runs end to end | 0 | 0 | n/a (design sprint) |
| 3 | 9–10 | @Nvhwng | P0 screens work end to end in the browser | not tracked | not tracked | not tracked |
| 4 | 11–12 | @phuonglinhtla | Every P0 story checked by `pytest`; fix the US06 cold-start genre bug | 30 | 30 | 30 |
| 5 | 13–14 | @KatsuroHuy | Public https URL, deploys only after green CI, operations documented | 30 | 27 | 27 |

Sprints 1–2 had no story points (requirements and design work) and Sprint 3 points were not tracked, so velocity is only meaningful for Sprints 4 and 5.

 ---

---

## Sprint N - <start date> to <end date>

<!-- Sprint 1: weeks 5-6 | Sprint 2: 7-8 | Sprint 3: 9-10 | Sprint 4: 11-12 | Sprint 5: 13-14 -->

### Sprint goal

<One sentence. If you cannot state the goal in one sentence, the sprint
has no goal and you are just doing tasks.>

### Hai chore issue bắt buộc

| Issue | Người làm | Đã đóng? |
|-------|-----------|----------|
| [Chore] Refine backlog cho Sprint N | @ | |
| [Chore] Sprint N wrap-up | @ (SM) | |

### Committed

| Issue | Story | Points | Owner |
|-------|-------|--------|-------|
| #     |       |        | @     |

**Total committed: __ points**

### Result

| Issue | Points | Status | If not done, why |
|-------|--------|--------|------------------|
| #     |        | Done / Carried over | |

**Completed: __ points. Velocity this sprint: __**

### Sprint Review

- What we demonstrated:
- Feedback received:
- Backlog changes as a result:

### Retrospective

| Keep doing | Stop doing | Start doing |
|------------|------------|-------------|
|            |            |             |

**One concrete action for next sprint (with an owner):**

<!-- A retro that produces no action item is a complaint session.
     Exactly one action, one owner, checked at the next retro. -->

### Attendance

| Member | Planning | Review | Retro |
|--------|----------|--------|-------|
| @      |          |        |       |




## Sprint 1 (weeks 5–6)
Goal: Agree on the product vision, personas, scenarios, business rules, and screens/flow so all 10 user stories are clear and testable before implementation begins.
Committed 0 · Completed 0 · Velocity: not applicable (requirements sprint)
Not finished: none.
SM Sprint 2: @th3dummyking


## Sprint 2 (weeks 7–8)
Goal: architecture, data model, API design and ADRs are documented, and one real route (walking skeleton) runs end-to-end against a seeded database.
Committed 0 · Completed 0 · Velocity: not applicable (design/skeleton sprint)
Not finished: none.
SM Sprint 3: @Nvhwng

## Sprint 3 (weeks 9–10)
Goal: the P0 screens work end to end in the browser (sign in, choose a profile, choose a genre, see recommendations, rate and mark movies as watched).
Committed: not tracked · Completed: not tracked · Velocity: not tracked
Not finished: US06 only partly works (the cold-start list ignores the chosen genre); landing page `/` not started.
SM Sprint 4: @phuonglinhtla

## Sprint 4 (weeks 11-12)

### Sprint goal
Every P0 story is checked by automated tests that run with one command (`pytest`), and the US06 bug found by those tests (cold-start ignores the chosen genre) is fixed.

### Hai chore issue bắt buộc

| Issue | Người làm | Đã đóng? |
|-------|-----------|----------|
| [Chore] Refine backlog for Sprint 4 (#99) | @KatsuroHuy (PO) |YES |
| [Chore] Sprint 4 wrap-up (#109) | @phuonglinhtla (SM) |YES |

### Committed

| Issue | Story | Points | Owner |
|-------|-------|--------|-------|
| #99 Refine backlog for Sprint 4 | process | 1 | @KatsuroHuy |
| #100 Expand seed data to 14 movies per genre | US01, US06 | 2 | @th3dummyking |
| #101 Shared test fixtures in tests/conftest.py | US01 | 2 | @Nvhwng |
| #102 Tests for US01 + US03 | US01, US03 | 5 | @Nvhwng |
| #103 Tests for US02 + US04 | US02, US04 | 5 | @th3dummyking |
| #104 Tests for US06 + US10 | US06, US10 | 3 | @KatsuroHuy |
| #105 Tests for the seed data and database constraints | US01 | 2 | @phuonglinhtla |
| #106 Bug: cold-start ignores the selected genre | US06 | 3 | @KatsuroHuy |
| #107 Write docs/testing.md and update SETUP.md | process | 5 | @phuonglinhtla |
| #108 Fill in the Sprint 4 section of sprint-log.md | process | 1 | @phuonglinhtla |
| #109 Sprint 4 wrap-up | process | 1 | @phuonglinhtla |

**Total committed: 30 points**

### Result

| Issue | Points | Status | If not done, why |
|-------|--------|--------|------------------|
| #99 | 1 |DONE | |
| #100 | 2 |DONE | |
| #101 | 2 |DONE | |
| #102 | 5 |DONE | |
| #103 | 5 |DONE | |
| #104 | 3 |DONE | |
| #105 | 2 |DONE | |
| #106 | 3 |DONE | |
| #107 | 5 |DONE | |
| #108 | 1 |DONE | |
| #109 | 1 |DONE | |

**Completed: 30 points. Velocity this sprint: 30**

### Sprint Review

- What we demonstrated:`python -m pytest -v` passes on a fresh clone; the cold-start genre bug (US06) was found by a test and fixed.
- Feedback received: none yet
- Backlog changes as a result: US05, US07, US08, US09 and the landing page `/` stay in the backlog for the next sprint.

### Retrospective

| Keep doing | Stop doing | Start doing |
|------------|------------|-------------|
| | | |

**One concrete action for next sprint (with an owner):** 
### Attendance

| Member | Planning | Review | Retro |
|--------|----------|--------|-------|
| @KatsuroHuy |YES | | |
| @Nvhwng |YES | | |
| @th3dummyking |YES | | |
| @phuonglinhtla |YES| | |



## Sprint 5 (weeks 13–14)

### Sprint goal
Anyone can open SmartCine at a public https URL; every merge to `main` is checked by CI and deployed only when CI is green; operations are documented.

Scrum Master: @KatsuroHuy

### Two required chore issues

| Issue | Owner | Closed? |
|-------|-------|---------|
| [Chore] Refine backlog for Sprint 5 (#__) | @KatsuroHuy (PO) | |
| [Chore] Sprint 5 wrap-up (#__) | @KatsuroHuy (SM) | |

### Committed

| Issue | Story | Points | Owner |
|-------|-------|--------|-------|
| #__ Refine backlog for Sprint 5 | process | 1 | @KatsuroHuy |
| #__ Add GET /health with tests | #23 | 2 | @phuonglinhtla |
| #__ Make CI check the frontend and fail on lint errors | #23 | 2 | @th3dummyking |
| #__ Deploy to a public https URL with deploy-after-green | #23 | 5 | @Nvhwng |
| #__ Protect `main` | #23 | 1 | @th3dummyking |
| #__ Refuse to start in production without JWT_SECRET | #23 | 2 | @phuonglinhtla |
| #__ Clear refusal messages when a business rule says no | #24 | 3 | @Nvhwng |
| #__ README first screen for the public URL | process | 2 | @phuonglinhtla |
| #__ docs/operations.md part 1 (sections 1 to 3) | #23 | 3 | @th3dummyking |
| #__ docs/operations.md part 2 (sections 4 to 6) | #23 | 3 | @Nvhwng |
| #__ Prepare and rehearse the final demo | process | 3 | @KatsuroHuy |
| #__ Release v1.0 on the deployed commit | #23 | 1 | @phuonglinhtla |
| #__ Sprint 5 section and five-sprint table in sprint-log.md | process | 1 | @KatsuroHuy |
| #__ Sprint 5 wrap-up | process | 1 | @KatsuroHuy |

**Total committed: 30 points**

### Result

| Issue | Points | Status | If not done, why |
|-------|--------|--------|------------------|
| #__ | 1 | Done | |
| #__ | 2 | Done | |
| #__ | 2 | Done | |
| #__ | 5 | Done | |
| #__ | 1 | Done | |
| #__ | 2 | Done | |
| #__ | 3 | Done | |
| #__ | 2 | Done | |
| #__ | 3 | Done | |
| #__ | 3 | Done | |
| #__ | 3 | In Progress | In a rush so we couldn't update the real status |
| #__ | 1 | Done | |
| #__ | 1 | Done | |
| #__ | 1 | Done | |

**Completed: 27 points. Velocity this sprint: 27**

### Sprint Review

- What we demonstrated:
- Feedback received:
- Backlog changes as a result:

### Retrospective

| Keep doing | Stop doing | Start doing |
|------------|------------|-------------|
| | | |

**One concrete action for next sprint (with an owner):**

### Attendance

| Member | Planning | Review | Retro |
|--------|----------|--------|-------|
| @KatsuroHuy | | | |
| @Nvhwng | | | |
| @th3dummyking | | | |
| @phuonglinhtla | | | |