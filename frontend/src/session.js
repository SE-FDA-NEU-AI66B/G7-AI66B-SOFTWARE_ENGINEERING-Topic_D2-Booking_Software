const KEY = "smartcine.session";

export function loadSession() {
  try {
    return JSON.parse(sessionStorage.getItem(KEY));
  } catch {
    return null;
  }
}

export function storeSession(session) {
  try {
    if (session) sessionStorage.setItem(KEY, JSON.stringify(session));
    else sessionStorage.removeItem(KEY);
  } catch {
    // Storage unavailable: the session lasts until the page reloads.
  }
}

export function authHeaders(session) {
  const headers = { Authorization: `Bearer ${session.access_token}` };
  if (session.profile) headers["X-Profile-Id"] = String(session.profile.id);
  return headers;
}