// All settings and business-rule numbers live here (BR1, BR3, BR4, BR5, BR8).
module.exports = {
  port: process.env.PORT || 3000,
  sessionSecret: process.env.SESSION_SECRET || 'dev-secret-change-me',
  rules: {
    maxRecommendations: 10,   // BR3
    minMovieRating: 6.0,      // BR4
    minPreferenceCount: 5,    // BR5
    minRatingCount: 100,      // BR8
    watchedThreshold: 0.9     // BR1 (90% of runtime)
  }
};
