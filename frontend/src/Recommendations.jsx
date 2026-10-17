import { useEffect, useState } from "react";

export default function Recommendations() {
  const [state, setState] = useState({ status: "loading", movies: [] });

  const load = () => {
    setState({ status: "loading", movies: [] });
    fetch("/api/v1/recommendations")
      .then((r) => {
        if (!r.ok) throw new Error();
        return r.json();
      })
      .then((movies) =>
        setState({ status: movies.length ? "data" : "empty", movies })
      )
      .catch(() => setState({ status: "error", movies: [] }));
  };

  useEffect(load, []);

  if (state.status === "loading") return <p>Loading recommendations...</p>;
  if (state.status === "error")
    return (
      <p>
        We can't reach the server. <button onClick={load}>Try again</button>
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