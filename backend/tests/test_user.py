"""User model tests: register, login, API key generation and storage."""
import uuid

import pytest
from fastapi.testclient import TestClient


def test_register(client: TestClient) -> None:
  email = f"register-{uuid.uuid4().hex}@example.com"
  resp = client.post(
    "/api/v1/auth/register",
    json={"email": email, "name": "Register User", "password": "password123"},
  )
  assert resp.status_code == 200
  data = resp.json()
  assert data["email"] == email
  assert data["name"] == "Register User"
  assert "id" in data
  assert "created_at" in data
  assert "password" not in data
  assert "password_hash" not in data
  assert "api_key_hash" not in data


def test_register_duplicate_email(client: TestClient) -> None:
  email = f"dup-{uuid.uuid4().hex}@example.com"
  client.post(
    "/api/v1/auth/register",
    json={"email": email, "name": "Dup", "password": "password123"},
  )
  resp = client.post(
    "/api/v1/auth/register",
    json={"email": email, "name": "Dup2", "password": "other456"},
  )
  assert resp.status_code == 400
  assert "already registered" in resp.json().get("detail", "").lower()


def test_login(client: TestClient) -> None:
  email = f"login-{uuid.uuid4().hex}@example.com"
  client.post(
    "/api/v1/auth/register",
    json={"email": email, "name": "Login User", "password": "password123"},
  )
  resp = client.post(
    "/api/v1/auth/login",
    json={"email": email, "password": "password123"},
  )
  assert resp.status_code == 200
  data = resp.json()
  assert "access_token" in data
  assert data.get("token_type") == "bearer"


def test_login_wrong_password(client: TestClient) -> None:
  email = f"wrong-{uuid.uuid4().hex}@example.com"
  client.post(
    "/api/v1/auth/register",
    json={"email": email, "name": "Wrong", "password": "password123"},
  )
  resp = client.post(
    "/api/v1/auth/login",
    json={"email": email, "password": "wrongpass"},
  )
  assert resp.status_code == 401


def test_me_with_bearer(client: TestClient, auth_headers: dict[str, str]) -> None:
  resp = client.get("/api/v1/users/me", headers=auth_headers)
  assert resp.status_code == 200
  data = resp.json()
  assert data["email"] == "test@example.com"
  assert data["name"] == "Test User"
  assert "id" in data


def test_me_unauthorized(client: TestClient) -> None:
  resp = client.get("/api/v1/users/me")
  assert resp.status_code == 401


def test_api_key_generate_and_storage(
  client: TestClient,
  auth_headers: dict[str, str],
  api_key_headers: tuple[dict[str, str], str],
) -> None:
  key_headers, plain_key = api_key_headers
  assert len(plain_key) > 0
  resp = client.get("/api/v1/users/me", headers=key_headers)
  assert resp.status_code == 200
  assert resp.json()["email"] == "test@example.com"


def test_api_key_invalid(client: TestClient) -> None:
  resp = client.get("/api/v1/users/me", headers={"X-API-Key": "invalid-key"})
  assert resp.status_code == 401
