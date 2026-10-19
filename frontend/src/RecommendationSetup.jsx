import { Link } from "react-router-dom";

// Placeholder: the real theme/companion form is built in the US06 issue.
function RecommendationSetup() {
  return (
    <main className="setup-page">
      <h1>What are you in the mood for?</h1>
      <p className="muted">Theme selection is coming soon. You can already see the default list.</p>
      <Link className="primary-link" to="/recommendations">
        See recommendations
      </Link>
    </main>
  );
}

export default RecommendationSetup;