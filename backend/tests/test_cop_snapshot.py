import time

from fastapi.testclient import TestClient


def test_snapshot_shape(client: TestClient, auth_headers):
    headers = auth_headers("commander", "commander123")
    resp = client.get("/api/v1/cop/snapshot", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    for key in ("bases", "aircraft", "airspace", "threats", "weatherCells", "routes"):
        assert key in body
        assert isinstance(body[key], list)
    assert "activePlan" in body
    assert len(body["bases"]) == 4
    assert len(body["aircraft"]) == 42


def test_snapshot_under_300ms(client: TestClient, auth_headers):
    headers = auth_headers("commander", "commander123")
    start = time.perf_counter()
    resp = client.get("/api/v1/cop/snapshot", headers=headers)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < 300, f"snapshot took {elapsed_ms:.1f}ms"


def test_kpis_shape(client: TestClient, auth_headers):
    headers = auth_headers("commander", "commander123")
    resp = client.get("/api/v1/kpis", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["aircraftTotal"] == 42
    assert 0 <= body["aircraftReady"] <= 42
    assert body["criticalAlerts"] == 0
