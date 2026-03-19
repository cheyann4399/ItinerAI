"""Itinerary model tests: create, list, get, update, JSONB content."""
import pytest
from fastapi.testclient import TestClient


def test_create_itinerary(client: TestClient, auth_headers: dict[str, str]) -> None:
  resp = client.post(
    "/api/v1/itineraries",
    headers=auth_headers,
    json={
      "title": "西安三日游",
      "description": "历史文化与美食",
      "content": {"days": 3, "cities": ["西安"], "tags": ["历史", "美食"]},
    },
  )
  assert resp.status_code == 201
  data = resp.json()
  assert data["title"] == "西安三日游"
  assert data["description"] == "历史文化与美食"
  assert data["content"] == {"days": 3, "cities": ["西安"], "tags": ["历史", "美食"]}
  assert "id" in data
  assert "user_id" in data
  assert "created_at" in data
  assert "updated_at" in data


def test_create_itinerary_minimal(client: TestClient, auth_headers: dict[str, str]) -> None:
  resp = client.post(
    "/api/v1/itineraries",
    headers=auth_headers,
    json={"title": "Minimal Trip"},
  )
  assert resp.status_code == 201
  data = resp.json()
  assert data["title"] == "Minimal Trip"
  assert data["description"] is None
  assert data["content"] is None


def test_list_itineraries(client: TestClient, auth_headers: dict[str, str]) -> None:
  client.post(
    "/api/v1/itineraries",
    headers=auth_headers,
    json={"title": "A", "content": {"x": 1}},
  )
  client.post(
    "/api/v1/itineraries",
    headers=auth_headers,
    json={"title": "B", "content": {"y": 2}},
  )
  resp = client.get("/api/v1/itineraries", headers=auth_headers)
  assert resp.status_code == 200
  items = resp.json()
  assert isinstance(items, list)
  titles = [it["title"] for it in items]
  assert "A" in titles
  assert "B" in titles
  assert items[0]["created_at"] >= items[1]["created_at"]


def test_get_itinerary(client: TestClient, auth_headers: dict[str, str]) -> None:
  create = client.post(
    "/api/v1/itineraries",
    headers=auth_headers,
    json={"title": "Get One", "content": {"nested": {"a": 1}}},
  )
  assert create.status_code == 201
  rid = create.json()["id"]
  resp = client.get(f"/api/v1/itineraries/{rid}", headers=auth_headers)
  assert resp.status_code == 200
  data = resp.json()
  assert data["id"] == rid
  assert data["title"] == "Get One"
  assert data["content"] == {"nested": {"a": 1}}


def test_get_itinerary_404(client: TestClient, auth_headers: dict[str, str]) -> None:
  resp = client.get("/api/v1/itineraries/999999", headers=auth_headers)
  assert resp.status_code == 404


def test_update_itinerary(client: TestClient, auth_headers: dict[str, str]) -> None:
  create = client.post(
    "/api/v1/itineraries",
    headers=auth_headers,
    json={"title": "Original", "description": "Desc", "content": {"v": 1}},
  )
  assert create.status_code == 201
  rid = create.json()["id"]
  created_at = create.json()["created_at"]
  updated_at_before = create.json()["updated_at"]
  resp = client.patch(
    f"/api/v1/itineraries/{rid}",
    headers=auth_headers,
    json={"title": "Updated", "content": {"v": 2, "extra": "jsonb"}},
  )
  assert resp.status_code == 200
  data = resp.json()
  assert data["title"] == "Updated"
  assert data["description"] == "Desc"
  assert data["content"] == {"v": 2, "extra": "jsonb"}
  assert data["created_at"] == created_at
  assert data["updated_at"] >= updated_at_before


def test_update_itinerary_partial(client: TestClient, auth_headers: dict[str, str]) -> None:
  create = client.post(
    "/api/v1/itineraries",
    headers=auth_headers,
    json={"title": "Partial", "content": {"keep": True}},
  )
  assert create.status_code == 201
  rid = create.json()["id"]
  resp = client.patch(
    f"/api/v1/itineraries/{rid}",
    headers=auth_headers,
    json={"description": "Only description changed"},
  )
  assert resp.status_code == 200
  data = resp.json()
  assert data["title"] == "Partial"
  assert data["description"] == "Only description changed"
  assert data["content"] == {"keep": True}


def test_jsonb_field_access(client: TestClient, auth_headers: dict[str, str]) -> None:
  payload = {
    "title": "JSONB Test",
    "content": {
      "days": [{"date": "2026-04-01", "pois": ["A", "B"]}],
      "budget": {"total": 5000, "currency": "CNY"},
    },
  }
  create = client.post("/api/v1/itineraries", headers=auth_headers, json=payload)
  assert create.status_code == 201
  data = create.json()
  assert data["content"] == payload["content"]
  get_one = client.get(f"/api/v1/itineraries/{data['id']}", headers=auth_headers)
  assert get_one.status_code == 200
  assert get_one.json()["content"] == payload["content"]
