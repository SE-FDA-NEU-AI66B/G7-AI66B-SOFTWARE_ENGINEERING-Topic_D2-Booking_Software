// Protects "U" (user) routes. Guests get sent to /login.
module.exports = function requireAuth(req, res, next) {
  if (!req.session.userEmail) return res.redirect('/login');
  next();
};
