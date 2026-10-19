import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import "./profiles.css";

// Read the API's error message; fall back to plain text if the body isn't usable.
async function readError(response, fallback) {
  try {
    const body = await response.json();
    return typeof body.detail === "string" ? body.detail : fallback;
  } catch {
    return fallback;
  }
}

export default function MovieDetail({ token, profileId }) {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [score, setScore] = useState("");
  const [status, setStatus] = useState({ kind: "loading", message: "Loading movie..." });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetch(`/api/v1/movies/${encodeURIComponent(id)}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "X-Profile-Id": String(profileId),
      },
    })
      .then(async (response) => {
        const body = await response.json();
        if (!response.ok) throw new Error(body.detail || "Could not load this movie.");
        return body;
      })
      .then((data) => {
        if (cancelled) return;
        setMovie(data);
        setScore(data.user_rating == null ? "" : String(data.user_rating));
        setStatus({ kind: "ready", message: "" });
      })
      .catch(() => {
        if (!cancelled)
          setStatus({ kind: "error", message: "We can't load this movie. Check your connection and try again." });
      });
    return () => {
      cancelled = true;
    };
  }, [id, token, profileId]);

  async function submitRating(event) {
    event.preventDefault();
    const value = Number(score);
    if (!Number.isInteger(value) || value < 1 || value > 10) {
      setStatus({ kind: "error", message: "Rating must be between 1 and 10." });
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
      if (!response.ok) {
        setStatus({
          kind: "error",
          message: await readError(response, "We couldn't save your rating. Please try again."),
        });
        return;
      }
      setMovie((current) => ({ ...current, user_rating: value, watched: true }));
      setStatus({ kind: "success", message: "Your rating has been saved." });
    } catch {
      setStatus({
        kind: "error",
        message: "We can't reach the server. Check your connection and try again.",
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
      if (!response.ok) {
        setStatus({
          kind: "error",
          message: await readError(response, "We couldn't mark this movie as watched. Please try again."),
        });
        return;
      }
      setMovie((current) => ({ ...current, watched: true }));
      setStatus({ kind: "success", message: "Marked as watched. It will no longer appear in your recommendations." });
    } catch {
      setStatus({
        kind: "error",
        message: "We can't reach the server. Check your connection and try again.",
      });
    } finally {
      setBusy(false);
    }
  }

  if (status.kind === "loading") return <main className="movie-detail-page"><p>{status.message}</p></main>;
  if (!movie) return <main className="movie-detail-page"><p role="alert">{status.message}</p><Link to="/recommendations">Back to recommendations</Link></main>;

  return (
    <main className="movie-detail-page">
      <Link to="/recommendations">← Back to recommendations</Link>
      <article className="movie-detail-card">
        <p className="movie-detail-kicker">{movie.genre}</p>
        <h1>{movie.title}</h1>
        <p className="muted">IMDb {movie.rating.toFixed(1)}/10 · {movie.rating_count.toLocaleString()} votes</p>
        {movie.imdb_id && <a href={`https://www.imdb.com/title/${movie.imdb_id}/`} target="_blank" rel="noreferrer">View on IMDb</a>}

        <form className="rating-form" onSubmit={submitRating}>
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
              {movie.user_rating == null ? "Save rating" : "Update rating"}
            </button>
          </div>
        </form>

        <button className="watched-button" type="button" onClick={markWatched} disabled={busy || movie.watched}>
          {movie.watched ? "Already watched" : "Mark as watched"}
        </button>
        {status.message && <p role={status.kind === "error" ? "alert" : "status"} className={status.kind === "error" ? "movie-message error" : "movie-message"}>{status.message}</p>}
      </article>
    </main>
  );
}
