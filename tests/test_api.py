import pytest

from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_ready_ok(client):
    assert client.get("/ready").status_code == 200


def test_ready_fails_when_db_down(client, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://x:y@localhost:1/none")
    assert client.get("/ready").status_code == 503


def test_create_incident(client):
    r = client.post("/incidents", json={"title": "disk full", "severity": "high"})
    assert r.status_code == 201
    assert r.get_json()["title"] == "disk full"


def test_list_incidents(client):
    client.post("/incidents", json={"title": "list-check", "severity": "low"})
    r = client.get("/incidents")
    assert r.status_code == 200
    assert any(i["title"] == "list-check" for i in r.get_json())


def test_rejects_empty_title(client):
    assert client.post("/incidents", json={"title": ""}).status_code == 400


def test_rejects_bad_severity(client):
    r = client.post("/incidents", json={"title": "x", "severity": "urgent"})
    assert r.status_code == 400
