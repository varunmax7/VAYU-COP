from fastapi.testclient import TestClient


def test_filter_aircraft_by_base(client: TestClient, auth_headers):
    headers = auth_headers("commander", "commander123")
    resp = client.get("/api/v1/aircraft", params={"base": "ALPHA"}, headers=headers)
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) > 0
    assert all(r["baseId"] == "ALPHA" for r in rows)


def test_filter_aircraft_by_type_and_status(client: TestClient, auth_headers):
    headers = auth_headers("commander", "commander123")
    resp = client.get(
        "/api/v1/aircraft", params={"type": "SU30", "status": "READY"}, headers=headers
    )
    assert resp.status_code == 200
    rows = resp.json()
    assert all(r["typeCode"] == "SU30" and r["status"] == "READY" for r in rows)


def test_aircraft_pagination(client: TestClient, auth_headers):
    headers = auth_headers("commander", "commander123")
    page1 = client.get("/api/v1/aircraft", params={"limit": 5, "offset": 0}, headers=headers)
    page2 = client.get("/api/v1/aircraft", params={"limit": 5, "offset": 5}, headers=headers)
    assert len(page1.json()) == 5
    assert len(page2.json()) == 5
    assert {a["id"] for a in page1.json()}.isdisjoint({a["id"] for a in page2.json()})


def test_filter_crew_by_base_and_type(client: TestClient, auth_headers):
    headers = auth_headers("commander", "commander123")
    resp = client.get("/api/v1/crew", params={"base": "BRAVO", "type": "RAF"}, headers=headers)
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) > 0
    assert all(r["baseId"] == "BRAVO" and "RAF" in r["qualifiedTypes"] for r in rows)


def test_filter_missions_by_priority(client: TestClient, auth_headers):
    headers = auth_headers("planner", "planner123")
    resp = client.get("/api/v1/missions", params={"priority": "P4_ROUTINE"}, headers=headers)
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) > 0
    assert all(r["priority"] == "P4_ROUTINE" for r in rows)


def test_get_nonexistent_aircraft_is_404(client: TestClient, auth_headers):
    headers = auth_headers("commander", "commander123")
    resp = client.get("/api/v1/aircraft/NOPE-99", headers=headers)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"
