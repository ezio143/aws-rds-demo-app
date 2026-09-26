from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

app = FastAPI(title="Order Tracking API")

# Creates the `orders` table if it doesn't exist yet. Fine for this
# project's scope; a real production app would use a migration tool
# (e.g. Alembic) instead of create_all so schema changes are tracked.
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    """Basic liveness check — doesn't touch the DB, just confirms the app is up."""
    return {"status": "ok"}


@app.post("/orders", response_model=schemas.OrderOut, status_code=201)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = models.Order(
        customer_name=order.customer_name,
        item_description=order.item_description,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.get("/orders", response_model=List[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()


@app.get("/orders/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.patch("/orders/{order_id}/status", response_model=schemas.OrderOut)
def update_order_status(
    order_id: str, update: schemas.OrderStatusUpdate, db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = update.status
    db.commit()
    db.refresh(order)
    return order
