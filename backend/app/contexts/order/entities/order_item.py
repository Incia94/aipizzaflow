from sqlalchemy import Column, Float, ForeignKey, Integer, JSON, String

from app.shared.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    base_selected = Column(String, nullable=False)
    toppings_selected = Column(JSON, nullable=False, default=list)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
