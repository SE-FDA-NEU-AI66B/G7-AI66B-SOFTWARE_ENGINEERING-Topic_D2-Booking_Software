// In-memory "database" for users, ratings and watched movies.
// Data resets when the server restarts. Swap for a real DB later.
const users = {};

function getUser(email) {
  if (!users[email]) {
    users[email] = {
      email,
      allowedRating: 15,   // BR2: max age rating this user may see
      ratings: {},         // { movieId: score 1-10 }
      watched: new Set()   // movie ids marked watched
    };
  }
  return users[email];
}

module.exports = { getUser };
