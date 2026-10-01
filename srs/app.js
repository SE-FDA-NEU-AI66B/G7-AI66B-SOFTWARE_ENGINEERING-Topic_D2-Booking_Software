// Builds the Express app: middleware + routes. No business logic here.
const path = require('path');
const express = require('express');
const session = require('express-session');
const config = require('./config');

const app = express();

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, '..', 'public')));
app.use(session({ secret: config.sessionSecret, resave: false, saveUninitialized: false }));

// Make the logged-in user available in every view.
app.use((req, res, next) => {
  res.locals.currentUser = req.session.userEmail || null;
  next();
});

app.use('/', require('./routes'));

app.use((req, res) => res.status(404).render('404', { title: 'Not found' }));

module.exports = app;
