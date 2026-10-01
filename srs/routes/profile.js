const router = require('express').Router();
const movieService = require('../services/movieService');

router.get('/ratings', (req, res) => {
  res.render('ratings', { title: 'My ratings', rated: movieService.getRatedMovies(req.session.userEmail) });
});

router.post('/ratings/:id/delete', (req, res) => {
  movieService.removeRating(req.session.userEmail, req.params.id);
  res.redirect('/profile/ratings');
});

module.exports = router;
