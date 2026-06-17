from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["provider"] == "Eburon AI"

def test_list_models():
    response = client.get("/v1/eburon/models/")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "Eburon AI"
    model_ids = [m["id"] for m in data["models"]]
    assert "talkhuman-3.1" in model_ids
    assert "translatehuman-3.1" in model_ids

def test_roleplay_model_exists():
    response = client.get("/v1/eburon/models/talkhuman-3.1")
    assert response.status_code == 200
    assert response.json()["provider"] == "Eburon AI"
    assert "realtime_expressive_voice" in response.json()["type"]

def test_translate_models():
    response = client.get("/v1/eburon/translate/models")
    assert response.status_code == 200
    assert response.json()["provider"] == "Eburon AI"
