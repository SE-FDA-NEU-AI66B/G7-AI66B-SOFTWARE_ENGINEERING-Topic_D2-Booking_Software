import { useEffect, useState } from "react";

export default function Recommendations({ token, profileId }) {
  const [state, setState] = useState({ status: "loading", movies: [] });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/v1/recommendations", {
      headers: { Authorization: `Bearer ${token}`, "X-Profile-Id": String(profileId) },
    })
      .then((r) => {
        if (!r.ok) throw new Error();
        return r.json();
      })
      .then((movies) => {
        if (!cancelled) setState({ status: movies.length ? "data" : "empty", movies });
      })
      .catch(() => {
        if (!cancelled) setState({ status: "error", movies: [] });
      });
    return () => {
      cancelled = true;
    };
  }, [attempt, token, profileId]);

  function retry() {
    setState({ status: "loading", movies: [] });
    setAttempt((n) => n + 1);
  }

  if (state.status === "loading") return <p>Loading recommendations...</p>;
  if (state.status === "error")
    return (
      <p>
        We can't reach the server. <button onClick={retry}>Try again</button>
      </p>
    );
  if (state.status === "empty") return <p>No recommendations yet.</p>;

  return (
    <div>
      <h1>Recommendations</h1>
      <table border="1">
        <thead>
          <tr><th>ID</th><th>Title</th><th>Genre</th><th>Rating</th></tr>
        </thead>
        <tbody>
          {state.movies.map((m) => (
            <tr key={m.id}>
              <td>{m.id}</td><td>{m.title}</td><td>{m.genre}</td><td>{m.rating}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}