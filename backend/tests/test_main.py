from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Mock redis et sqlalchemy avant l'import de main
sys.modules['redis'] = MagicMock()

with patch('sqlalchemy.create_engine') as mock_engine:
    mock_conn = MagicMock()
    mock_engine.return_value.connect.return_value.__enter__ = lambda s: mock_conn
    mock_engine.return_value.connect.return_value.__exit__ = MagicMock(return_value=False)
    
    from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend OK"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_movies_sans_token():
    with patch.dict(os.environ, {"TMDB_TOKEN": ""}):
        from app import main
        main.TMDB_TOKEN = ""
        response = client.get("/movies")
        assert response.status_code == 500

def test_search_sans_token():
    with patch.dict(os.environ, {"TMDB_TOKEN": ""}):
        from app import main
        main.TMDB_TOKEN = ""
        response = client.get("/search?q=batman")
        assert response.status_code == 500