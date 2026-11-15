"""Tests for the production JWT_SECRET check (Sprint 5, issue #123).

In production (APP_ENV=production) the app must refuse to start when
JWT_SECRET is missing or shorter than 32 characters.
"""

import pytest

from auth import validate_jwt_secret


def test_production_without_jwt_secret_refuses_to_start(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        validate_jwt_secret()


def test_production_with_short_jwt_secret_refuses_to_start(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "x" * 31)  # one character too short

    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        validate_jwt_secret()


def test_production_with_long_enough_jwt_secret_starts(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)  # exactly the minimum

    validate_jwt_secret()  # must not raise


def test_development_without_jwt_secret_still_starts(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("JWT_SECRET", raising=False)

    validate_jwt_secret()  # local runs keep using the dev secret