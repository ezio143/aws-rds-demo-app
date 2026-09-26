import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.mysql import CHAR

from database import Base


class OrderStatus(str, enum.Enum):
    placed = "placed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_name = Column(String(120), nullable=False)
    item_description = Column(String(255), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.placed, nullable=False)
    created_at = Column(DateTime, default=datetime.timezone.utc)
    updated_at = Column(DateTime, default=datetime.timezone.utc, onupdate=datetime.timezone.utc)
