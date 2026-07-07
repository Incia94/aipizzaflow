from sqlalchemy import Boolean, Column, Numeric, String

from app.shared.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(String, primary_key=True, index=True)
    category = Column(String, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
