const router = require('express').Router();
const { getRecommendations } = require('../services/recommendationService');

const GENRES = ['romance', 'thriller', 'horror', 'drama', 'mystery', 'sci-fi', 'musical'];

router.get('/setup', (req, res) => res.render('setup', { title: 'Find a movie', genres: GENRES }));

router.post('/setup', (req, res) => {
  const genres = [].concat(req.body.genres || []);
  req.session.prefs = { genres, withOthers: req.body.withOthers === 'group' };
  res.redirect('/recommendations');
});

router.get('/', (req, res) => {
  if (!req.session.prefs) return res.redirect('/recommendations/setup');
  const result = getRecommendations(req.session.userEmail, req.session.prefs);
  res.render('recommendations', { title: 'Recommendations', prefs: req.session.prefs, ...result });
});

module.exports = router;
