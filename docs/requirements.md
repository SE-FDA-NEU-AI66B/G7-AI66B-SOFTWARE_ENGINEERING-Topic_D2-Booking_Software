# Group 07 - Movie Recommendation System - Requirements

## 1. Product vision

## 2. Personas

## 3. Scenarios

## 4. User stories

## 5. Business rules

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
