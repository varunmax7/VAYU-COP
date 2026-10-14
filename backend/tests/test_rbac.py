from fastapi.testclient import TestClient

_THREAT_PAYLOAD = {
    "label": "T-99",
    "level": "LOW",
    "centerLat": 20.0,
    "centerLon": 78.0,
    "radiusKm": 10,
}


def test_aircrew_cannot_patch_aircraft_status(client: TestClient, auth_headers):
    headers = auth_headers("crew", "crew123")  # AIRCREW role
    resp = client.patch(
        "/api/v1/aircraft/SU30-01/status", json={"status": "MAINTENANCE"}, headers=headers
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


def test_maintenance_can_patch_aircraft_status(client: TestClient, auth_headers):
    headers = auth_headers("maint", "maint123")  # MAINTENANCE role
    resp = client.patch(
        "/api/v1/aircraft/SU30-02/status", json={"status": "MAINTENANCE"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "MAINTENANCE"


def test_planner_cannot_approve_role_restricted_threat_write(client: TestClient, auth_headers):
    headers = auth_headers("planner", "planner123")  # PLANNER role, threats need INTEL
    resp = client.post("/api/v1/threats", json=_THREAT_PAYLOAD, headers=headers)
    assert resp.status_code == 403


def test_intel_can_create_threat(client: TestClient, auth_headers):
    headers = auth_headers("intel", "intel123")  # INTEL role
    resp = client.post("/api/v1/threats", json=_THREAT_PAYLOAD, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["label"] == "T-99"


def test_all_authenticated_roles_can_read(client: TestClient, auth_headers):
    headers = auth_headers("crew", "crew123")
    resp = client.get("/api/v1/aircraft", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) > 0


def test_unauthenticated_write_is_401_not_403(client: TestClient):
    resp = client.patch("/api/v1/aircraft/SU30-01/status", json={"status": "READY"})
    assert resp.status_code == 401
