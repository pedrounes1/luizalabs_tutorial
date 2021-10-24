from fastapi.testclient import TestClient
from http import HTTPStatus
import pytest
from api_pedidos.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_integrity_status_code_200(client):
    response = client.get("/healthcheck")
    assert response.status_code == HTTPStatus.OK


def test_integrity_response_type_is_json(client):
    response = client.get("/healthcheck")
    assert response.headers['Content-Type'] == 'application/json'


def test_integrity_response_content(client):
    response = client.get("/healthcheck")
    assert response.json() == {"status": "ok", }
