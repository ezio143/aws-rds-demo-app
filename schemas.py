from datetime import datetime

from pydantic import BaseModel

from models import OrderStatus


class OrderCreate(BaseModel):
    customer_name: str
    item_description: str


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderOut(BaseModel):
    id: str
    customer_name: str
    item_description: str
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # lets Pydantic read straight off the SQLAlchemy object
