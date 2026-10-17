"""Authentication: password hashing, JWT, and POST /api/v1/auth/login."""

import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

PBKDF2_ITERATIONS = 200_000
TOKEN_TTL_MINUTES = 60

# Seeded TEST account (fake credentials, documented in docs/SETUP.md).
TEST_EMAIL = "demo@smartcine.test"
TEST_PASSWORD = "Demo@1234"
TEST_PROFILES = [("Alex", "#F5C518"), ("Sam", "#5799EF")]


def get_conn() -> sqlite3.Connection:
    # Read DB_PATH on every call so tests can point to a temporary database.
    conn = sqlite3.connect(os.environ.get("DB_PATH", "data/smartcine.db"))
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iterations, salt, digest = stored.split("$")
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), int(iterations)
        ).hex()
    except ValueError:
        return False
    return hmac.compare_digest(candidate, digest)


# Used to keep response time similar when the email does not exist.
_DUMMY_HASH = hash_password("not-a-real-password")


def ensure_schema_and_seed(conn: sqlite3.Connection) -> None:
    """Create account/profile tables and insert the test account. Safe to re-run."""
    conn.executescript(
        """
        DROP TABLE IF EXISTS profile;
        DROP TABLE IF EXISTS account;
        CREATE TABLE account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL REFERENCES account(id),
            name TEXT NOT NULL,
            avatar_color TEXT NOT NULL
        );
        """
    )
    cur = conn.execute(
        "INSERT INTO account (email, password_hash) VALUES (?, ?)",
        (TEST_EMAIL, hash_password(TEST_PASSWORD)),
    )
    conn.executemany(
        "INSERT INTO profile (account_id, name, avatar_color) VALUES (?, ?, ?)",
        [(cur.lastrowid, name, color) for name, color in TEST_PROFILES],
    )
    conn.commit()


def create_access_token(account_id: int) -> str:
    secret = os.environ.get(
        "JWT_SECRET", "dev-only-secret-change-me-in-env-0123456789"
    )
    now = datetime.now(UTC)
    payload = {
        "sub": str(account_id),
        "iat": now,
        "exp": now + timedelta(minutes=TOKEN_TTL_MINUTES),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


class LoginRequest(BaseModel):
    email: str = ""
    password: str = ""


@router.post("/login")
def login(body: LoginRequest):
    email = body.email.strip().lower()
    if not email or not body.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")

    conn = get_conn()
    try:
        account = conn.execute(
            "SELECT id, password_hash FROM account WHERE email = ?", (email,)
        ).fetchone()
        stored = account["password_hash"] if account else _DUMMY_HASH
        valid = verify_password(body.password, stored)
        if not account or not valid:
            raise HTTPException(status_code=401, detail="Incorrect email or password.")
        profiles = conn.execute(
            "SELECT id, name, avatar_color FROM profile WHERE account_id = ? ORDER BY id",
            (account["id"],),
        ).fetchall()
    finally:
        conn.close()

    return {
        "access_token": create_access_token(account["id"]),
        "token_type": "bearer",
        "profiles": [dict(p) for p in profiles],
    }