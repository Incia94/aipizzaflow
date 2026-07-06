from typing import Optional

from sqlalchemy.orm import Session

from app.contexts.reference.entities.menu_item import MenuItem


class MenuRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_available_items(self) -> list[MenuItem]:
        return self._db.query(MenuItem).filter(MenuItem.is_available == True).all()

    def get_by_id(self, item_id: int) -> Optional[MenuItem]:
        return self._db.query(MenuItem).filter(MenuItem.id == item_id).first()

    def count(self) -> int:
        return self._db.query(MenuItem).count()

    def save_items(self, items: list[MenuItem]) -> None:
        self._db.add_all(items)
        self._db.commit()
