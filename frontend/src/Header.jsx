import { Link } from "react-router-dom";
import "./profiles.css";

function Header({ session, onSignOut }) {
  const { profile } = session;
  return (
    <header className="app-header">
      <span className="logo small">SmartCine</span>
      <nav>
        <span className="avatar tiny" style={{ background: profile.avatar_color }} aria-hidden="true">
          {profile.name[0]}
        </span>
        <span className="who">{profile.name}</span>
        <Link to="/profiles">Switch profile</Link>
        <button type="button" onClick={onSignOut}>
          Sign out
        </button>
      </nav>
    </header>
  );
}

export default Header;