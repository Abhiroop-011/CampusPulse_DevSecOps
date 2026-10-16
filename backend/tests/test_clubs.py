"""
Tests for the /api/clubs endpoints.
Covers: GET list, GET single, POST create, PUT update, DELETE, conflict, and 404.
"""
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def create_club(client, slug="test-club", name="Test Club", category="TECH"):
    return client.post("/api/clubs", json={
        "name": name,
        "slug": slug,
        "description": "A test club",
        "category": category,
        "lead_email": "lead@test.edu",
    })


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def test_list_clubs_empty(client):
    response = client.get("/api/clubs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def test_create_club_success(client):
    response = create_club(client)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Club"
    assert data["slug"] == "test-club"
    assert data["category"] == "TECH"
    assert "id" in data
    assert "created_at" in data


def test_create_club_duplicate_slug_returns_409(client):
    create_club(client, slug="dupe-slug")
    response = create_club(client, slug="dupe-slug", name="Another Club")
    assert response.status_code == 409


def test_create_club_invalid_slug_returns_422(client):
    response = client.post("/api/clubs", json={
        "name": "Bad Slug Club",
        "slug": "has spaces and CAPS",
        "category": "TECH",
    })
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def test_get_club_by_id(client):
    created = create_club(client, slug="read-club")
    club_id = created.json()["id"]
    response = client.get(f"/api/clubs/{club_id}")
    assert response.status_code == 200
    assert response.json()["id"] == club_id


def test_get_club_not_found_returns_404(client):
    response = client.get("/api/clubs/99999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def test_update_club_description(client):
    club_id = create_club(client, slug="update-club").json()["id"]
    response = client.put(f"/api/clubs/{club_id}", json={"description": "Updated desc"})
    assert response.status_code == 200
    assert response.json()["description"] == "Updated desc"


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def test_delete_club_success(client):
    club_id = create_club(client, slug="delete-club").json()["id"]
    delete_resp = client.delete(f"/api/clubs/{club_id}")
    assert delete_resp.status_code == 200
    get_resp = client.get(f"/api/clubs/{club_id}")
    assert get_resp.status_code == 404


def test_delete_nonexistent_club_returns_404(client):
    response = client.delete("/api/clubs/88888")
    assert response.status_code == 404
