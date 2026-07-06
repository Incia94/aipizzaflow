from typing import Optional

from sqlalchemy.orm import Session

from app.contexts.order.entities.customer import Customer
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem
from app.contexts.order.schemas.order_schemas import CustomerRequest


class OrderRepository:
    def __init__(self, db: Session):
        self._db = db

    def find_customer_by_phone(self, phone_number: str) -> Optional[Customer]:
        return self._db.query(Customer).filter(Customer.phone_number == phone_number).first()

    def save_customer(self, customer_data: CustomerRequest) -> Customer:
        customer = Customer(name=customer_data.name, phone_number=customer_data.phone_number)
        self._db.add(customer)
        self._db.commit()
        self._db.refresh(customer)
        return customer

    def save_order(self, customer_id: int) -> Order:
        order = Order(customer_id=customer_id, status="pending")
        self._db.add(order)
        self._db.commit()
        self._db.refresh(order)
        return order

    def save_order_items(self, items: list[OrderItem]) -> list[OrderItem]:
        self._db.add_all(items)
        self._db.commit()
        for item in items:
            self._db.refresh(item)
        return items
