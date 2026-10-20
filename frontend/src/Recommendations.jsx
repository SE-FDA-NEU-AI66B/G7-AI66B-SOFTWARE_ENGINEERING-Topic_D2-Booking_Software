import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import "./profiles.css";

export default function Recommendations({ token, profileId }) {
  const [state, setState] = useState({ status: "loading", movies: [], mode: null });
  const [attempt, setAttempt] = useState(0);
  const [params] = useSearchParams();
  const genreId = params.get("genre_id");

  useEffect(() => {
    let cancelled = false;
    const query = genreId ? `?genre_id=${encodeURIComponent(genreId)}` : "";
    fetch(`/api/v1/recommendations${query}`, {
      headers: { Authorization: `Bearer ${token}`, "X-Profile-Id": String(profileId) },
    })
      .then((r) => {
        if (!r.ok) {
          if (r.status === 503)
            return r.json().then((body) => {
              if (body.detail?.code === "COLD_START_UNAVAILABLE") {
                return { noCandidates: true };
              }
              throw new Error();
            });
          throw new Error();
        }
        return r.json().then((movies) => ({
          movies,
          mode: r.headers.get("X-Recommendation-Mode"),
        }));
      })
      .then((result) => {
        if (cancelled) return;
        if (result.noCandidates) {
          setState({ status: "no-candidates", movies: [], mode: null });
        } else {
          setState({
            status: result.movies.length ? "data" : "empty",
            movies: result.movies,
            mode: result.mode,
          });
        }
      })
      .catch(() => {
        if (!cancelled) setState({ status: "error", movies: [], mode: null });
      });
    return () => {
      cancelled = true;
    };
  }, [attempt, token, profileId, genreId]);

  function retry() {
    setState({ status: "loading", movies: [], mode: null });
    setAttempt((n) => n + 1);
  }

  if (state.status === "loading") return <p>Loading recommendations...</p>;
  if (state.status === "error")
    return (
      <p>
        We can't reach the server. <button onClick={retry}>Try again</button>
      </p>
    );
  if (state.status === "empty")
    return (
      <p>
        {genreId ? `No movies found for "${genreId}".` : "No recommendations yet."}{" "}
        <Link to="/recommendations/setup">Choose another genre</Link>
      </p>
    );
  if (state.status === "no-candidates")
    return (
      <p role="alert">
        No movies currently qualify for the cold-start list (at least 100 ratings).{" "}
        <Link to="/recommendations/setup">Try again later</Link>
      </p>
    );

  return (
    <div>
      <h1>
        {state.mode === "cold-start" ? "Trending recommendations" : "Picked for you"}
        {state.mode !== "cold-start" && genreId ? `: ${genreId}` : ""}
      </h1>
      <p><Link to="/recommendations/setup">Change genre</Link></p>
      {state.mode === "cold-start" && (
        <p className="muted">
          Rate or watch at least 5 movies to get picks matched to your taste.
          Until then, these are the most-voted movies for everyone.
        </p>
      )}
      <table className="movie-table">
        <thead>
          <tr><th>Title</th><th>Genre</th><th>IMDb rating</th><th>IMDb votes</th></tr>
        </thead>
        <tbody>
          {state.movies.map((m) => (
            <tr key={m.id}>
              <td><Link to={`/movie/${m.id}`}>{m.title}</Link></td>
              <td>{m.genre}</td><td>{m.rating.toFixed(1)}/10</td><td>{m.rating_count.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}