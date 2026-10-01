from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["graph_loaded"] is True


def test_graph_stats():
    r = client.get("/api/v1/graph/stats")
    assert r.status_code == 200
    body = r.json()
    assert body["banana_count"] == 5
    assert body["products"] >= 25


def test_banana_check():
    r = client.get("/api/v1/banana-check")
    assert r.status_code == 200
    assert r.json()["status"] == "PASS"


def test_query_endpoint():
    r = client.post(
        "/api/v1/query",
        json={"question": "How many banana products are present in the knowledge graph?"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["retrieved_data"]["count"] == 5


def test_query_invalid_payload():
    r = client.post("/api/v1/query", json={"question": ""})
    assert r.status_code == 422
