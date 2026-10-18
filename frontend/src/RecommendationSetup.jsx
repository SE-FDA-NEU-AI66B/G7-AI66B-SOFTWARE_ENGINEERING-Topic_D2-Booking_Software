import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authHeaders } from "./session.js";
import "./profiles.css";

// US06: ask for a theme/genre before showing any movies.
function RecommendationSetup({ session, onSignOut }) {
  const navigate = useNavigate();
  const [state, setState] = useState({ status: "loading", genres: [] });
  const [selected, setSelected] = useState("");

  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/v1/recommendations/setup/genres", { headers: authHeaders(session) })
      .then((res) => {
        if (res.status === 401) {
          onSignOut();
          return null;
        }
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((genres) => {
        if (genres && !cancelled) setState({ status: genres.length ? "data" : "empty", genres });
      })
      .catch(() => {
        if (!cancelled) setState({ status: "error", genres: [] });
      });
    return () => {
      cancelled = true;
    };
  }, [attempt, session, onSignOut]);

  function load() {
    setState({ status: "loading", genres: [] });
    setAttempt((n) => n + 1);
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!selected) return;
    navigate(`/recommendations?genre_id=${encodeURIComponent(selected)}`);
  }

  return (
    <main className="setup-page">
      <h1>What are you in the mood for?</h1>

      {state.status === "loading" && <p className="muted">Loading genres…</p>}

      {state.status === "error" && (
        <div role="alert" className="login-error">
          We can't load the genres.{" "}
          <button type="button" className="link" onClick={load}>
            Try again
          </button>
        </div>
      )}

      {state.status === "empty" && (
        <p className="muted">No genres are available yet. Please check back later.</p>
      )}

      {state.status === "data" && (
        <form onSubmit={handleSubmit} className="genre-form">
          <div className="genre-list" role="group" aria-label="Genre">
            {state.genres.map((g) => (
              <button
                type="button"
                key={g.id}
                aria-pressed={selected === g.id}
                className={`genre-chip${selected === g.id ? " selected" : ""}`}
                onClick={() => setSelected(g.id)}
              >
                {g.name}
              </button>
            ))}
          </div>
          <button type="submit" className="primary-link" disabled={!selected}>
            Continue
          </button>
          {!selected && <p className="muted">Pick a genre to continue.</p>}
        </form>
      )}
    </main>
  );
}

export default RecommendationSetup;