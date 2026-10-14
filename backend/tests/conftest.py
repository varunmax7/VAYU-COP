import pytest
from app.main import app
from app.seed.generator import run as run_seed
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def seeded_db():
    """Seed the VAYU SHIELD scenario once for the whole test session."""
    run_seed(scenario_name="vayu_shield", do_reset=True)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient):
    def _make(username: str, password: str) -> dict[str, str]:
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": username, "password": password},
        )
        resp.raise_for_status()
        token = resp.json()["accessToken"]
        return {"Authorization": f"Bearer {token}"}

    return _make
