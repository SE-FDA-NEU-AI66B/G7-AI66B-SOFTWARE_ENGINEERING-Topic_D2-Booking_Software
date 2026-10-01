// Central route table. Add a new page = add one line here.
const router = require('express').Router();
const requireAuth = require('../middleware/requireAuth');

router.get('/', (req, res) => res.render('index', { title: 'SmartCine' }));

router.use('/', require('./auth'));                                        // /login, /logout
router.use('/recommendations', requireAuth, require('./recommendations')); // /recommendations[/setup]
router.use('/movie', requireAuth, require('./movie'));                     // /movie/:id
router.use('/profile', requireAuth, require('./profile'));                 // /profile/ratings

module.exports = router;
