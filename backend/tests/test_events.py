"""
Tests for /api/events endpoints.
Covers: list, create, read, update (including capacity guard), delete,
event registration, cancellation, and capacity enforcement.
"""
from datetime import datetime, timedelta, timezone

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FUTURE = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()


def make_club(client, slug="evt-club"):
    r = client.post("/api/clubs", json={
        "name": "Event Test Club",
        "slug": slug,
        "category": "TECH",
    })
    assert r.status_code == 201
    return r.json()["id"]


def make_event(client, club_id, title="Test Event", capacity=10, status="PUBLISHED"):
    r = client.post("/api/events", json={
        "club_id": club_id,
        "title": title,
        "description": "A test event",
        "location": "Room 101",
        "event_date": FUTURE,
        "capacity": capacity,
        "status": status,
    })
    return r


def register(client, event_id, email="student@campus.edu", name="Test Student"):
    return client.post(f"/api/events/{event_id}/registrations", json={
        "student_name": name,
        "student_email": email,
        "student_id": "STU001",
    })


# ---------------------------------------------------------------------------
# List events
# ---------------------------------------------------------------------------

def test_list_events_returns_list(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# Create event
# ---------------------------------------------------------------------------

def test_create_event_success(client):
    club_id = make_club(client, slug="create-evt-club")
    r = make_event(client, club_id, title="My Event")
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "My Event"
    assert data["club_id"] == club_id
    assert data["capacity"] == 10
    assert data["registered_count"] == 0
    assert data["spots_remaining"] == 10


def test_create_event_with_nonexistent_club_returns_404(client):
    r = make_event(client, club_id=99999)
    assert r.status_code == 404


def test_create_event_with_invalid_capacity_returns_422(client):
    club_id = make_club(client, slug="bad-cap-club")
    r = client.post("/api/events", json={
        "club_id": club_id,
        "title": "Bad Event",
        "event_date": FUTURE,
        "capacity": 0,  # invalid: must be >= 1
    })
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Read event
# ---------------------------------------------------------------------------

def test_get_event_by_id(client):
    club_id = make_club(client, slug="read-evt-club")
    event_id = make_event(client, club_id).json()["id"]
    r = client.get(f"/api/events/{event_id}")
    assert r.status_code == 200
    assert r.json()["id"] == event_id


def test_get_nonexistent_event_returns_404(client):
    r = client.get("/api/events/77777")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Update event
# ---------------------------------------------------------------------------

def test_update_event_title(client):
    club_id = make_club(client, slug="upd-evt-club")
    event_id = make_event(client, club_id).json()["id"]
    r = client.put(f"/api/events/{event_id}", json={"title": "Updated Title"})
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Title"


def test_update_event_status_to_published(client):
    club_id = make_club(client, slug="pub-evt-club")
    event_id = make_event(client, club_id, status="DRAFT").json()["id"]
    r = client.put(f"/api/events/{event_id}", json={"status": "PUBLISHED"})
    assert r.status_code == 200
    assert r.json()["status"] == "PUBLISHED"


def test_update_event_capacity_below_registrations_returns_422(client):
    club_id = make_club(client, slug="cap-guard-club")
    event_id = make_event(client, club_id, capacity=5).json()["id"]
    # Register 2 students first
    register(client, event_id, email="a@campus.edu")
    register(client, event_id, email="b@campus.edu")
    # Attempt to shrink capacity below registered count
    r = client.put(f"/api/events/{event_id}", json={"capacity": 1})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Delete event
# ---------------------------------------------------------------------------

def test_delete_event(client):
    club_id = make_club(client, slug="del-evt-club")
    event_id = make_event(client, club_id).json()["id"]
    r = client.delete(f"/api/events/{event_id}")
    assert r.status_code == 200
    assert client.get(f"/api/events/{event_id}").status_code == 404


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def test_register_for_event_success(client):
    club_id = make_club(client, slug="reg-club")
    event_id = make_event(client, club_id, capacity=20).json()["id"]
    r = register(client, event_id)
    assert r.status_code == 201
    data = r.json()
    assert data["student_email"] == "student@campus.edu"
    assert data["status"] == "CONFIRMED"


def test_registration_increments_registered_count(client):
    club_id = make_club(client, slug="cnt-club")
    event_id = make_event(client, club_id, capacity=20).json()["id"]
    register(client, event_id)
    event = client.get(f"/api/events/{event_id}").json()
    assert event["registered_count"] == 1
    assert event["spots_remaining"] == 19


def test_duplicate_registration_returns_409(client):
    club_id = make_club(client, slug="dup-reg-club")
    event_id = make_event(client, club_id, capacity=20).json()["id"]
    register(client, event_id, email="dup@campus.edu")
    r = register(client, event_id, email="dup@campus.edu")
    assert r.status_code == 409


def test_registration_on_full_event_returns_422(client):
    club_id = make_club(client, slug="full-evt-club")
    event_id = make_event(client, club_id, capacity=1).json()["id"]
    register(client, event_id, email="first@campus.edu")
    r = register(client, event_id, email="second@campus.edu")
    assert r.status_code == 422


def test_registration_on_draft_event_returns_422(client):
    club_id = make_club(client, slug="draft-reg-club")
    event_id = make_event(client, club_id, status="DRAFT").json()["id"]
    r = register(client, event_id)
    assert r.status_code == 422


def test_cancel_registration(client):
    club_id = make_club(client, slug="cancel-reg-club")
    event_id = make_event(client, club_id, capacity=10).json()["id"]
    reg_id = register(client, event_id).json()["id"]
    r = client.delete(f"/api/events/{event_id}/registrations/{reg_id}")
    assert r.status_code == 200
    # Registered count should have decremented
    event = client.get(f"/api/events/{event_id}").json()
    assert event["registered_count"] == 0


def test_invalid_email_registration_returns_422(client):
    club_id = make_club(client, slug="inv-email-club")
    event_id = make_event(client, club_id, capacity=10).json()["id"]
    r = client.post(f"/api/events/{event_id}/registrations", json={
        "student_name": "Bad Email",
        "student_email": "not-an-email",
    })
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Stats endpoint
# ---------------------------------------------------------------------------

def test_stats_endpoint_returns_expected_shape(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_events" in data
    assert "total_clubs" in data
    assert "total_registrations" in data
    assert "published_events" in data
    assert "average_capacity_utilization" in data
