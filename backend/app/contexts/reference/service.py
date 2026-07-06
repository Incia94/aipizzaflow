import csv

from app.contexts.reference.entities.menu_item import MenuItem
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.contexts.reference.schemas.menu_schemas import MenuItemResponse, MenuResponse


class MenuLoader:
    def __init__(self, repository: MenuRepository):
        self._repository = repository

    def load_menu(self) -> MenuResponse:
        items = self._repository.get_available_items()
        return MenuResponse(
            items=[
                MenuItemResponse(
                    id=item.id,
                    name=item.name,
                    category=item.category,
                    available_bases=item.available_bases,
                    available_toppings=item.available_toppings,
                    price=item.price,
                )
                for item in items
            ]
        )

    def seed_from_file(self, filepath: str) -> None:
        if self._repository.count() > 0:
            return

        items = []
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                items.append(
                    MenuItem(
                        name=row["name"],
                        category=row["category"],
                        available_bases=row["available_bases"].split("|"),
                        available_toppings=row["available_toppings"].split("|"),
                        price=float(row["price"]),
                        is_available=True,
                    )
                )

        self._repository.save_items(items)
