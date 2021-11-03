from http import HTTPStatus
import os
from uuid import UUID
from api_pedidos.schemas import Item
from api_pedidos.exceptions import OrderNotFoundError, CommunicationFailError

import httpx

APIKEY = os.environ.get("API_KEY", "5734143a-595d-405d-9c97-6c198537108f")
TENANT_ID = os.environ.get("TENANT_ID", "21fea73c-e244-497a-8540-be0d3c583596")
MAGALU_API_URL = "http://127.0.0.1:8080"
MAESTRO_SERVICE_URL = f"{MAGALU_API_URL}/maestro/v1"


def _get_items_by_package(order_id, package_id):
    response = httpx.get(f"{MAESTRO_SERVICE_URL}/orders/{order_id}/packages/{package_id}/items",
                         headers={"X-Api-Key": APIKEY, "X-Tenant-Id": TENANT_ID},)
    response.raise_for_status()
    return [
        Item(
            sku=item["product"]['code'],
            description=item['product'].get("description", ""),
            image_url=item['product'].get("image_url", ""),
            reference=item['product'].get("reference", ""),
            quantity=item["quantity"])
        for item in response.json()
    ]


def get_items_by_order(order_id: UUID) -> list[Item]:
    try:
        response = httpx.get(
            f"{MAESTRO_SERVICE_URL}/orders/{order_id}",
            headers={"X-Api-Key": APIKEY, "X-Tenant-Id": TENANT_ID})
        print(order_id,'\n\n\n')
        print(response)
        response.raise_for_status()
        packages = response.json()['packages']
        items = []
        for package in packages:
            items.extend(
                _get_items_by_package(order_id, package["uuid"])
            )
        return items
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == HTTPStatus.NOT_FOUND:
            raise OrderNotFoundError() from exc
        raise exc
    except httpx.HTTPError as exc:
        raise CommunicationFailError() from exc
