from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from uuid import UUID
from api_pedidos.api_magalu import get_items_by_order
from api_pedidos.schemas import ErrorResponse, Item, HealthCheckResponse
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


@app.get("/healthcheck", tags=["healthcheck"], summary="System integrity", description="Verify if server is on", response_model=HealthCheckResponse)
async def healthcheck():
    return HealthCheckResponse(status="Ok")


@app.get("/orders/{order_id}/items", responses={
HTTPStatus.NOT_FOUND.value: {
    "description": "Order not found",
    "model": ErrorResponse
},
HTTPStatus.BAD_GATEWAY.value: {
    "description": "Communication with remote server failed",
    "model": ErrorResponse
}
}, tags=["orders"], summary="Items of an order", description="Return all items of a given order", response_model=list[Item])
async def list_items(items: list[Item] = Depends(get_items_by_order)):
    return items
