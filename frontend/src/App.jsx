import { useCallback, useState } from "react";
import { HashRouter, Navigate, Route, Routes } from "react-router-dom";
import Header from "./Header.jsx";
import Login from "./Login.jsx";
import Profiles from "./Profiles.jsx";
import Recommendations from "./Recommendations.jsx";
import RecommendationSetup from "./RecommendationSetup.jsx";
import { loadSession, storeSession } from "./session.js";

function App() {
  const [session, setSession] = useState(loadSession);

  function update(next) {
    storeSession(next);
    setSession(next);
  }

  const signOut = useCallback(() => {
    storeSession(null);
    setSession(null);
  }, []);
  const handleLoggedIn = (data) => update({ ...data, profile: null });
  const handleSelect = (profile) => update({ ...session, profile });

  // Guards: no session -> /login; session without a profile -> /profiles.
  function requireProfile(page) {
    if (!session) return <Navigate to="/login" replace />;
    if (!session.profile) return <Navigate to="/profiles" replace />;
    return (
      <>
        <Header session={session} onSignOut={signOut} />
        {page}
      </>
    );
  }

  return (
    <HashRouter>
      <Routes>
        <Route
          path="/login"
          element={
            session ? <Navigate to="/profiles" replace /> : <Login onLoggedIn={handleLoggedIn} />
          }
        />
        <Route
          path="/profiles"
          element={
            session ? (
              <Profiles session={session} onSelect={handleSelect} onSignOut={signOut} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/recommendations/setup"
          element={requireProfile(<RecommendationSetup />)}
        />
        <Route
          path="/recommendations"
          element={requireProfile(
            session?.profile ? (
              <Recommendations token={session.access_token} profileId={session.profile.id} />
            ) : null
          )}
        />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </HashRouter>
  );
}

export default App;