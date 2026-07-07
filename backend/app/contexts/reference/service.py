from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.contexts.reference.schemas.menu_schemas import MenuItemResponse, MenuResponse


class MenuLoader:
    def __init__(self, repository: MenuRepository):
        self._repository = repository

    def load_menu(self) -> MenuResponse:
        items = self._repository.get_available_items()

        pizzas = []
        bases = []
        toppings = []

        for item in items:
            response = MenuItemResponse(
                id=item.id,
                category=item.category,
                name=item.name,
                price=float(item.price),
            )

            if item.category == "pizza":
                pizzas.append(response)
            elif item.category == "base":
                bases.append(response)
            elif item.category == "topping":
                toppings.append(response)

        return MenuResponse(
            pizzas=pizzas,
            bases=bases,
            toppings=toppings,
        )
