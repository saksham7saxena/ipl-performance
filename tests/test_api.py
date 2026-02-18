from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/api/players")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_player_stats():
    # Assuming player_id 1 (MS Dhoni usually has a low ID or high ID depending on dataset, let's try to query first player)
    # But for test, we can query list first then get ID
    response = client.get("/api/players?limit=1")
    if len(response.json()) > 0:
        pid = response.json()[0]['player_id']
        stats_response = client.get(f"/api/players/{pid}/stats")
        assert stats_response.status_code == 200
        assert "runs" in stats_response.json()
