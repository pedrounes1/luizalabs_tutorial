from http import HTTPStatus
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from api_pedidos.api import app
from api_pedidos.api_magalu import get_items_by_order
from api_pedidos.exceptions import CommunicationFailError, OrderNotFoundError
from api_pedidos.schemas import Item


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def overrides_get_items_by_order():
    def _overrides_get_items_by_order(items_or_error):
        def duble(order_id: UUID) -> list[Item]:
            if isinstance(items_or_error, Exception):
                raise items_or_error
            return items_or_error

        app.dependency_overrides[get_items_by_order] = duble

    yield _overrides_get_items_by_order
    app.dependency_overrides.clear()


class TestHealthCheck:
    def test_integrity_status_code_200(self, client):
        response = client.get("/healthcheck")
        assert response.status_code == HTTPStatus.OK

    def test_integrity_response_type_is_json(self, client):
        response = client.get("/healthcheck")
        assert response.headers["Content-Type"] == "application/json"

    def test_integrity_response_content(self, client):
        response = client.get("/healthcheck")
        assert response.json() == {
            "status": "ok",
        }


class TestListOrders:
    def test_return_error_on_invalid_id(self, client):
        response = client.get("/orders/invalid-value/items")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_not_found_order_should_return_error(
        self, client, overrides_get_items_by_order
    ):
        overrides_get_items_by_order(OrderNotFoundError())
        resposta = client.get(
            "/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items"
        )
        assert resposta.status_code == HTTPStatus.NOT_FOUND

    def test_found_should_return_ok_code(
        self, client, overrides_get_items_by_order
    ):
        overrides_get_items_by_order([])
        response = client.get(
            "/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items"
        )
        assert response.status_code == HTTPStatus.OK

    def test_found_shoud_return_items(
        self, client, overrides_get_items_by_order
    ):
        items = [
            Item(
                sku="1",
                description="Item 1",
                image_url="http://url.com/img1",
                reference="ref1",
                quantity="1",
            ),
            Item(
                sku="2",
                description="Item 2",
                image_url="http://url.com/img2",
                reference="ref2",
                quantity="2",
            ),
        ]

        overrides_get_items_by_order(items)
        response = client.get(
            "/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items"
        )
        assert response.json() == items


class TestMagaluAPI:
    def test_communication_fail(self, client, overrides_get_items_by_order):
        overrides_get_items_by_order(CommunicationFailError())
        response = client.get(
            "/orders/ea78b59b-885d-4e7b-9cd0-d54acadb4933/items"
        )
        assert response.status_code == HTTPStatus.BAD_GATEWAY
