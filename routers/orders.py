from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

class Order(BaseModel):
    product_id: int
    quantity: int = 1
    comment: Optional[str] = None

@router.post("/", status_code=201)
async def create_order(order: Order):
    return {"order": order, "total_price": order.product_id * order.quantity}