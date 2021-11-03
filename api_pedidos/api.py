from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from uuid import UUID
from api_pedidos.api_magalu import get_items_by_order
from api_pedidos.schemas import Item
from api_pedidos.exceptions import CommunicationFailError, OrderNotFoundError
from http import HTTPStatus


app = FastAPI()


# def get_items_by_order(order_id: UUID) -> list[Item]:
#     pass


@app.exception_handler(OrderNotFoundError)
def handle_not_found(request: Request, exc: OrderNotFoundError):
    return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"message": "Order not found =("})


@app.exception_handler(CommunicationFailError)
def handle_communication_fail(request: Request, exc: CommunicationFailError):
    return JSONResponse(status_code=HTTPStatus.BAD_GATEWAY, content={"message": "Communication with server failed"})


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.get("/orders/{order_id}/items")
async def list_items(items: list[Item] = Depends(get_items_by_order)):
    return items
