# SmartCine - walking skeleton

Smallest end-to-end slice: Landing -> Login -> Setup -> Recommendations -> Movie detail -> My ratings.
Data is in memory (resets on restart). Login accepts any email.

## Run
    npm install
    npm start        # http://localhost:3000   (npm run dev = auto-reload)

## Structure
    src/
      server.js        starts the server
      app.js           middleware + mounts routes
      config/          settings + business-rule numbers (BR1-BR9)
      routes/          one file per URL area (thin)
      middleware/      requireAuth (guards "U" routes)
      services/        logic (recommendations, rating, watched)
      data/            fake movies + in-memory store  <- swap for DB later
      utils/           pure helper functions, one per business rule
      views/           EJS pages + partials (header/footer)
    public/css/        static files

## Routes
    /                        G  landing
    /login                   G  sign in
    /recommendations/setup   U  who + topics
    /recommendations         U  list (personalized or cold-start)
    /movie/:id               U  detail, mark watched, rate
    /profile/ratings         U  manage ratings (P1)

## Adding a new page
1. Add a route in src/routes/<area>.js (or a new file + one line in routes/index.js)
2. Put logic in src/services/
3. Add a view in src/views/
