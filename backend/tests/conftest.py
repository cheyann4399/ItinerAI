import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
  return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
  client.post(
    "/api/v1/auth/register",
    json={"email": "test@example.com", "name": "Test User", "password": "password123"},
  )
  login_resp = client.post(
    "/api/v1/auth/login",
    json={"email": "test@example.com", "password": "password123"},
  )
  assert login_resp.status_code == 200
  token = login_resp.json()["access_token"]
  return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def api_key_headers(client: TestClient, auth_headers: dict[str, str]) -> tuple[dict[str, str], str]:
  resp = client.post("/api/v1/users/me/api-key", headers=auth_headers)
  assert resp.status_code == 200
  api_key = resp.json()["api_key"]
  return ({"X-API-Key": api_key}, api_key)
