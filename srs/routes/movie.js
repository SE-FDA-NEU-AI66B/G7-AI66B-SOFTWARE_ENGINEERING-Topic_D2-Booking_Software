const router = require('express').Router();
const movieService = require('../services/movieService');
const { getUser } = require('../data/store');

router.get('/:id', (req, res, next) => {
  const movie = movieService.getMovieById(req.params.id);
  if (!movie) return next(); // falls through to 404
  const user = getUser(req.session.userEmail);
  res.render('movie', {
    title: movie.title,
    movie,
    watched: user.watched.has(movie.id),
    myScore: user.ratings[movie.id]
  });
});

router.post('/:id/watched', (req, res) => {
  movieService.markWatched(req.session.userEmail, req.params.id);
  res.redirect(`/movie/${req.params.id}`);
});

router.post('/:id/rate', (req, res) => {
  const score = Math.min(10, Math.max(1, Number(req.body.score)));
  if (score) movieService.rateMovie(req.session.userEmail, req.params.id, score);
  res.redirect(`/movie/${req.params.id}`);
});

module.exports = router;
