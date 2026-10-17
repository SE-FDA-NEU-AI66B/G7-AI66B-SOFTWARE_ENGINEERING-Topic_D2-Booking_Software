import { useState } from "react";
import Login from "./Login.jsx";
import Recommendations from "./Recommendations.jsx";

function readSession() {
  try {
    return JSON.parse(sessionStorage.getItem("smartcine.session"));
  } catch {
    return null;
  }
}

function App() {
  const [session, setSession] = useState(readSession);

  function handleLoggedIn(data) {
    try {
      sessionStorage.setItem("smartcine.session", JSON.stringify(data));
    } catch {
      /* storage unavailable: session lasts until reload */
    }
    setSession(data);
  }

  function signOut() {
    try {
      sessionStorage.removeItem("smartcine.session");
    } catch {
      /* ignore */
    }
    setSession(null);
  }

  if (!session) return <Login onLoggedIn={handleLoggedIn} />;

  return (
    <div>
      <button onClick={signOut}>Sign out</button>
      <Recommendations />
    </div>
  );
}

export default App;