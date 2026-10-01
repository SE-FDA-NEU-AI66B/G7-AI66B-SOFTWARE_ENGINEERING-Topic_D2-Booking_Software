const router = require('express').Router();
const { getUser } = require('../data/store');

router.get('/login', (req, res) => res.render('login', { title: 'Sign in' }));

// Skeleton auth: any email works. Replace with real sign in / sign up later.
router.post('/login', (req, res) => {
  const email = (req.body.email || '').trim().toLowerCase();
  if (!email) return res.redirect('/login');
  getUser(email);
  req.session.userEmail = email;
  res.redirect('/recommendations/setup');
});

router.post('/logout', (req, res) => req.session.destroy(() => res.redirect('/')));

module.exports = router;
