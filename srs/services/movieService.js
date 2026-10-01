const movies = require('../data/movies');
const { getUser } = require('../data/store');

const getMovieById = (id) => movies.find((m) => m.id === Number(id));

function rateMovie(email, movieId, score) {
  getUser(email).ratings[movieId] = score;
}

function markWatched(email, movieId) {
  getUser(email).watched.add(Number(movieId));
}

function getRatedMovies(email) {
  const user = getUser(email);
  return Object.entries(user.ratings).map(([id, score]) => ({ ...getMovieById(id), myScore: score }));
}

function removeRating(email, movieId) {
  delete getUser(email).ratings[movieId];
}

module.exports = { getMovieById, rateMovie, markWatched, getRatedMovies, removeRating };
