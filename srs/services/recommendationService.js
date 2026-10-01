const movies = require('../data/movies');
const { getUser } = require('../data/store');
const { rules } = require('../config');
const r = require('../utils/rules');

// TODO: replace with real collaborative filtering later.
// For now: score = movie rating, boosted by how many chosen genres match.
function predictScore(movie, genres) {
  const matches = movie.genres.filter((g) => genres.includes(g)).length;
  return movie.rating + matches;
}

function getRecommendations(email, prefs = {}) {
  const user = getUser(email);
  const genres = prefs.genres || [];
  const personalized = r.hasEnoughPreferenceData(user);        // BR5 / BR6

  const pool = movies
    .filter((m) => !r.isWatched(user, m))                      // BR1
    .filter((m) => r.isAllowedAge(user, m))                    // BR2
    .filter(personalized ? r.meetsMinRating : r.meetsMinRatingCount); // BR4 / BR8

  const ranked = pool
    .map((m) => ({ ...m, score: predictScore(m, genres) }))
    .sort(r.compareMovies);                                    // BR9

  return {
    mode: personalized ? 'personalized' : 'cold-start',
    movies: r.uniqueById(ranked).slice(0, rules.maxRecommendations) // BR7 / BR3
  };
}

module.exports = { getRecommendations };
