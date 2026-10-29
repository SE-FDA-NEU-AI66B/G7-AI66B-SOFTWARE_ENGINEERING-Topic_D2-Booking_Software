# Sprint log

One section per sprint. Fill it in **during** the sprint, not the night before
the milestone deadline - the commit timestamps on this file are part of the
evidence that the process was real.

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

## Sprint 4(weeks 11-12)

### Sprint goal
Every P0 story is checked by automated tests that run with one command (`pytest`), and the US06 bug found by those tests (cold-start ignores the chosen genre) is fixed.

### Hai chore issue bắt buộc

| Issue | Người làm | Đã đóng? |
|-------|-----------|----------|
| [Chore] Refine backlog for Sprint 4 (#99) | @KatsuroHuy (PO) | |
| [Chore] Sprint 4 wrap-up (#109) | @phuonglinhtla (SM) | |

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
| #99 | 1 | | |
| #100 | 2 | | |
| #101 | 2 | | |
| #102 | 5 | | |
| #103 | 5 | | |
| #104 | 3 | | |
| #105 | 2 | | |
| #106 | 3 | | |
| #107 | 5 | | |
| #108 | 1 | | |
| #109 | 1 | | |

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

### Attendance

| Member | Planning | Review | Retro |
|--------|----------|--------|-------|
| @KatsuroHuy | | | |
| @Nvhwng | | | |
| @th3dummyking | | | |
| @phuonglinhtla | | | |