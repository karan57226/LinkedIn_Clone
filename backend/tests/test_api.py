import os
import tempfile
from pathlib import Path

TEST_DB = Path(tempfile.gettempdir()) / "mini_professional_network_test.db"
TEST_DB.unlink(missing_ok=True)

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["FRONTEND_ORIGIN"] = "http://localhost:5173"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_health_endpoint_reports_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "test"}


def test_feed_endpoint_returns_seeded_posts() -> None:
    with TestClient(app) as client:
        response = client.get("/api/feed")

    assert response.status_code == 200
    posts = response.json()
    assert len(posts) >= 3
    assert {"Maya Chen", "Noah Patel", "Ava Williams"}.issubset(
        {post["author"]["name"] for post in posts}
    )


def test_can_create_profile() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/profiles",
            json={
                "name": "Sam Rivera",
                "title": "Site Reliability Engineer",
                "location": "Perth, WA",
            },
        )

    assert response.status_code == 201
    profile = response.json()
    assert profile["name"] == "Sam Rivera"
    assert profile["title"] == "Site Reliability Engineer"


def test_can_create_post_for_existing_profile() -> None:
    with TestClient(app) as client:
        profiles_response = client.get("/api/profiles")
        author_id = profiles_response.json()[0]["id"]

        response = client.post(
            "/api/posts",
            json={
                "author_id": author_id,
                "body": "Testing a write path from the API to the database.",
            },
        )

    assert response.status_code == 201
    post = response.json()
    assert post["body"] == "Testing a write path from the API to the database."
    assert post["author"]["id"] == author_id
