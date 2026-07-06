from sqlalchemy import Boolean, Column, Float, Integer, JSON, String

from app.shared.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    available_bases = Column(JSON, nullable=False)
    available_toppings = Column(JSON, nullable=False)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
