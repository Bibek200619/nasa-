# tests/conftest.py
import os
import secrets
import pytest

# Import the application factory
from app import create_app

@pytest.fixture(scope="session")
def test_env():
    """
    Load environment for tests and ensure required variables are present.
    Override in CI or per-test using monkeypatch_env.
    """
    # Ensure a dummy but strong secret for signed cookies during tests
    os.environ.setdefault("SECRET_KEY", secrets.token_hex(32))
    # Provide a default test API key if not set
    os.environ.setdefault("NASA_API_KEY", "TEST_NASA_KEY")
    return {
        "SECRET_KEY": os.environ["SECRET_KEY"],
        "NASA_API_KEY": os.environ["NASA_API_KEY"],
    }

@pytest.fixture(scope="session")
def app(test_env):
    """
    Create a Flask app configured for testing using the factory pattern.
    """
    # Build the app via the factory and inject testing config
    app = create_app()
    app.config.update(
        TESTING=True,                  # enables testing behaviors
        SECRET_KEY=test_env["SECRET_KEY"],  # signed session cookies
        NASA_API_KEY=test_env["NASA_API_KEY"],  # used by services
    )

    # Push one application context for the session if desired
    ctx = app.app_context()
    ctx.push()

    yield app

    # Teardown
    ctx.pop()

@pytest.fixture()
def client(app):
    """
    Flask test client for request/response tests.
    """
    return app.test_client()

@pytest.fixture()
def runner(app):
    """
    Flask CLI runner to test Click commands.
    """
    return app.test_cli_runner()

@pytest.fixture()
def monkeypatch_env(monkeypatch):
    """
    Helper to temporarily set environment variables within a test.
    Usage:
        def test_thing(monkeypatch_env, client):
            monkeypatch_env({"NASA_API_KEY": "OVERRIDE"})
            ...
    """
    def setter(env_map):
        for k, v in env_map.items():
            monkeypatch.setenv(k, v)
    return setter
