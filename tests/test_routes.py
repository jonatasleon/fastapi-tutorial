import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(name="client")
def fixture_client():
    """Fixture for test client."""
    yield TestClient(app)


def test_home(client: TestClient):
    """Test home page."""
    response = client.get("/")
    assert response.status_code == 404, "Status code is not 404"


def test_users_me(client: TestClient):
    """Test users/me."""
    response = client.get("/users/me")
    assert response.status_code == 401, "Status code is not 401"


def test_items(client: TestClient):
    """Test items."""
    response = client.get("/items")
    assert response.status_code == 401, "Status code is not 401"