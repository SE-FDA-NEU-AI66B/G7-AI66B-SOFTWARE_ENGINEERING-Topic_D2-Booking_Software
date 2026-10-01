// Small pure functions, one per business rule. Easy to test and extend.
const { rules } = require('../config');

// BR1: exclude watched movies
const isWatched = (user, movie) => user.watched.has(movie.id);

// BR2: age rating must not be higher than allowed (equal is OK)
const isAllowedAge = (user, movie) => movie.ageRating <= user.allowedRating;

// BR4: personalized pool needs rating >= 6.0
const meetsMinRating = (movie) => movie.rating >= rules.minMovieRating;

// BR8: cold-start pool needs >= 100 ratings
const meetsMinRatingCount = (movie) => movie.ratingCount >= rules.minRatingCount;

// BR5: personalized only if >= 5 rated or watched movies
const hasEnoughPreferenceData = (user) =>
  new Set([...Object.keys(user.ratings).map(Number), ...user.watched]).size >= rules.minPreferenceCount;

// BR9: tie-break by score desc, then ratingCount desc, then year desc
const compareMovies = (a, b) =>
  b.score - a.score || b.ratingCount - a.ratingCount || b.year - a.year;

// BR7: unique ids
const uniqueById = (movies) => [...new Map(movies.map((m) => [m.id, m])).values()];

module.exports = {
  isWatched, isAllowedAge, meetsMinRating, meetsMinRatingCount,
  hasEnoughPreferenceData, compareMovies, uniqueById
};
