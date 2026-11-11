import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import "./profiles.css";

const MOVIE_NOT_FOUND = "This movie does not exist. Go back to the list and choose another movie.";
const RATING_OUT_OF_RANGE =
  "Your rating was not saved. Ratings must be between 1 and 10. Choose a number from 1 to 10 and press Save rating.";

export default function MovieDetail({ token, profileId, onSignOut }) {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [loadedId, setLoadedId] = useState(null);
  const [score, setScore] = useState("");
  const [status, setStatus] = useState({ kind: "loading", message: "Loading movie..." });
  const [busy, setBusy] = useState(false);
  const [attempt, setAttempt] = useState(0);

  function retryLoad() {
    setStatus({ kind: "loading", message: "Loading movie..." });
    setAttempt((current) => current + 1);
  }

  useEffect(() => {
    let cancelled = false;
    fetch(`/api/v1/movies/${encodeURIComponent(id)}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "X-Profile-Id": String(profileId),
      },
    })
      .then(async (response) => {
        if (response.status === 401) {
          if (!cancelled) onSignOut("Your session has expired. Sign in again.");
          return null;
        }
        if (response.status === 404) {
          if (!cancelled) {
            setLoadedId(id);
            setStatus({ kind: "error", message: MOVIE_NOT_FOUND });
          }
          return null;
        }
        if (!response.ok) throw new Error();
        return response.json();
      })
      .then((data) => {
        if (cancelled || !data) return;
        setMovie(data);
        setLoadedId(id);
        setScore(data.user_rating == null ? "" : String(data.user_rating));
        setStatus({ kind: "ready", message: "" });
      })
      .catch(() => {
        if (!cancelled) {
          setLoadedId(id);
          setStatus({
            kind: "error",
            message: "We can't reach the server. Try again.",
            retry: retryLoad,
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [id, token, profileId, onSignOut, attempt]);

  async function submitRating() {
    const value = Number(score);
    if (!Number.isInteger(value) || value < 1 || value > 10) {
      setStatus({ kind: "error", message: RATING_OUT_OF_RANGE });
      return;
    }

    setBusy(true);
    try {
      const response = await fetch("/api/v1/ratings", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "X-Profile-Id": String(profileId),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ movie_id: movie.id, score: value }),
      });
      if (response.status === 401) {
        onSignOut("Your session has expired. Sign in again.");
        return;
      }
      if (response.status === 400) {
        setStatus({ kind: "error", message: RATING_OUT_OF_RANGE });
        return;
      }
      if (response.status === 404) {
        setStatus({ kind: "error", message: MOVIE_NOT_FOUND });
        return;
      }
      if (!response.ok) {
        setStatus({
          kind: "error",
          message: "Your rating was not saved. The server couldn't complete the request. Try again.",
          retry: submitRating,
        });
        return;
      }
      setMovie((current) => ({ ...current, user_rating: value, watched: true }));
      setStatus({ kind: "success", message: "Your rating has been saved." });
    } catch {
      setStatus({
        kind: "error",
        message: "We can't reach the server. Try again.",
        retry: submitRating,
      });
    } finally {
      setBusy(false);
    }
  }

  async function markWatched() {
    setBusy(true);
    try {
      const response = await fetch(`/api/v1/movies/${encodeURIComponent(id)}/watch`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "X-Profile-Id": String(profileId),
        },
      });
      if (response.status === 401) {
        onSignOut("Your session has expired. Sign in again.");
        return;
      }
      if (response.status === 404) {
        setStatus({ kind: "error", message: MOVIE_NOT_FOUND });
        return;
      }
      if (!response.ok) {
        setStatus({
          kind: "error",
          message: "We couldn't mark this movie as watched. The server couldn't complete the request. Try again.",
          retry: markWatched,
        });
        return;
      }
      setMovie((current) => ({ ...current, watched: true }));
      setStatus({ kind: "success", message: "Marked as watched. It will no longer appear in your recommendations." });
    } catch {
      setStatus({
        kind: "error",
        message: "We can't reach the server. Try again.",
        retry: markWatched,
      });
    } finally {
      setBusy(false);
    }
  }

  function handleRatingSubmit(event) {
    event.preventDefault();
    void submitRating();
  }

  const currentMovie = movie && String(movie.id) === id ? movie : null;
  if (status.kind === "loading" || loadedId !== id)
    return <main className="movie-detail-page"><p>Loading movie...</p></main>;
  if (!currentMovie)
    return (
      <main className="movie-detail-page">
        <p role="alert">{status.message}</p>
        {status.retry && (
          <button type="button" className="link" onClick={status.retry}>
            Try again
          </button>
        )}
        <Link to="/recommendations">Back to recommendations</Link>
      </main>
    );

  return (
    <main className="movie-detail-page">
      <Link to="/recommendations">← Back to recommendations</Link>
      <article className="movie-detail-card">
        <p className="movie-detail-kicker">{currentMovie.genre}</p>
        <h1>{currentMovie.title}</h1>
        <p className="muted">IMDb {currentMovie.rating.toFixed(1)}/10 · {currentMovie.rating_count.toLocaleString()} votes</p>
        {currentMovie.imdb_id && <a href={`https://www.imdb.com/title/${currentMovie.imdb_id}/`} target="_blank" rel="noreferrer">View on IMDb</a>}

        <form className="rating-form" onSubmit={handleRatingSubmit}>
          <label htmlFor="movie-rating">Your rating (1–10)</label>
          <div className="rating-controls">
            <select
              id="movie-rating"
              value={score}
              onChange={(event) => setScore(event.target.value)}
              disabled={busy}
              required
            >
              <option value="" disabled>Select a rating</option>
              {Array.from({ length: 10 }, (_, index) => index + 1).map((rating) => (
                <option key={rating} value={rating}>{rating}</option>
              ))}
            </select>
            <button className="primary-link" type="submit" disabled={busy}>
              {currentMovie.user_rating == null ? "Save rating" : "Update rating"}
            </button>
          </div>
        </form>

        <button className="watched-button" type="button" onClick={markWatched} disabled={busy || currentMovie.watched}>
          {currentMovie.watched ? "Already watched" : "Mark as watched"}
        </button>
        {status.message && (
          <div role={status.kind === "error" ? "alert" : "status"} className={status.kind === "error" ? "movie-message error" : "movie-message"}>
            <p>{status.message}</p>
            {status.retry && (
              <button type="button" className="link" onClick={status.retry} disabled={busy}>
                Try again
              </button>
            )}
          </div>
        )}
      </article>
    </main>
  );
}
