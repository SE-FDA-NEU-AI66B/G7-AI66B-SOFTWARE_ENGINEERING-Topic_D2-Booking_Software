import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authHeaders } from "./session.js";
import "./profiles.css";

function Profiles({ session, onSelect, onSignOut }) {
  const navigate = useNavigate();
  const [state, setState] = useState({ status: "loading", profiles: [] });
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);

  const token = session.access_token;
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/v1/profiles", { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        if (res.status === 401) {
          onSignOut();
          return null;
        }
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((profiles) => {
        if (profiles && !cancelled) {
          setState({ status: profiles.length ? "data" : "empty", profiles });
        }
      })
      .catch(() => {
        if (!cancelled) setState({ status: "error", profiles: [] });
      });
    return () => {
      cancelled = true;
    };
  }, [attempt, token, onSignOut]);

  function retry() {
    setState({ status: "loading", profiles: [] });
    setAttempt((n) => n + 1);
  }



  async function choose(profile) {
    setError("");
    setBusyId(profile.id);
    try {
      const res = await fetch("/api/v1/profiles/select", {
        method: "POST",
        headers: { ...authHeaders(session), "Content-Type": "application/json" },
        body: JSON.stringify({ profile_id: profile.id }),
      });
      if (res.status === 401) {
        onSignOut();
        return;
      }
      if (res.status === 404) {
        setError("That profile is not part of this account. Reload the page and try again.");
        return;
      }
      if (!res.ok) throw new Error();
      onSelect(await res.json());
      navigate("/recommendations/setup");
    } catch {
      setError("Can't reach the server. Check that it is running, then try again.");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <main className="profiles-page">
      <div className="logo">SmartCine</div>
      <h1>Who's watching?</h1>

      {state.status === "loading" && <p className="muted">Loading profiles…</p>}

      {state.status === "error" && (
        <p className="muted" role="alert">
          We can't load your profiles.{" "}
          <button type="button" className="link" onClick={retry}>
            Try again
          </button>
        </p>
      )}

      {state.status === "empty" && (
        <p className="muted">This account has no profiles yet. Ask the account owner to add one.</p>
      )}

      {error && (
        <div className="login-error" role="alert">
          {error}
        </div>
      )}

      {state.status === "data" && (
        <ul className="profile-grid">
          {state.profiles.map((p) => (
            <li key={p.id}>
              <button
                type="button"
                className="profile-card"
                onClick={() => choose(p)}
                disabled={busyId !== null}
              >
                <span className="avatar" style={{ background: p.avatar_color }} aria-hidden="true">
                  {p.name[0]}
                </span>
                <span className="profile-name">{busyId === p.id ? "Opening…" : p.name}</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      <button type="button" className="link" onClick={onSignOut}>
        Sign out
      </button>
    </main>
  );
}

export default Profiles;