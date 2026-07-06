from datetime import datetime

from sqlalchemy.orm import Session

from app.contexts.analytics.schemas.analytics_schemas import AnalyticsRequest
from app.contexts.checkout.entities.bill import Bill
from app.contexts.checkout.entities.payment import Payment
from app.contexts.order.entities.customer import Customer
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem


class AnalyticsRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_paid_orders(self, filters: AnalyticsRequest) -> list[Order]:
        query = self._db.query(Order).filter(Order.status == "paid")

        if filters.from_date:
            query = query.filter(Order.updated_at >= datetime.combine(filters.from_date, datetime.min.time()))
        if filters.to_date:
            query = query.filter(Order.updated_at <= datetime.combine(filters.to_date, datetime.max.time()))
        if filters.customer_id:
            query = query.filter(Order.customer_id == filters.customer_id)

        orders = query.all()

        if filters.payment_method:
            paid_order_ids = {o.id for o in orders}
            matching_payments = (
                self._db.query(Payment.order_id)
                .filter(Payment.order_id.in_(paid_order_ids), Payment.payment_method == filters.payment_method)
                .all()
            )
            matching_ids = {row.order_id for row in matching_payments}
            orders = [o for o in orders if o.id in matching_ids]

        if filters.pizza_id or filters.category:
            order_ids = {o.id for o in orders}
            item_query = self._db.query(OrderItem.order_id).filter(OrderItem.order_id.in_(order_ids))
            if filters.pizza_id:
                item_query = item_query.filter(OrderItem.menu_item_id == filters.pizza_id)
            matching_ids = {row.order_id for row in item_query.all()}

            if filters.category:
                from app.contexts.reference.entities.menu_item import MenuItem
                cat_item_ids = {
                    row.id
                    for row in self._db.query(MenuItem.id).filter(MenuItem.category == filters.category).all()
                }
                cat_order_ids = {
                    row.order_id
                    for row in self._db.query(OrderItem.order_id)
                    .filter(OrderItem.order_id.in_(order_ids), OrderItem.menu_item_id.in_(cat_item_ids))
                    .all()
                }
                matching_ids = matching_ids & cat_order_ids if filters.pizza_id else cat_order_ids

            orders = [o for o in orders if o.id in matching_ids]

        return orders

    def get_order_items(self, order_ids: list[int]) -> list[OrderItem]:
        if not order_ids:
            return []
        return self._db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).all()

    def get_bills(self, order_ids: list[int]) -> list[Bill]:
        if not order_ids:
            return []
        return self._db.query(Bill).filter(Bill.order_id.in_(order_ids)).all()

    def get_customers(self, customer_ids: list[int]) -> list[Customer]:
        if not customer_ids:
            return []
        return self._db.query(Customer).filter(Customer.id.in_(customer_ids)).all()

    def get_payments(self, order_ids: list[int]) -> list[Payment]:
        if not order_ids:
            return []
        return self._db.query(Payment).filter(Payment.order_id.in_(order_ids)).all()
