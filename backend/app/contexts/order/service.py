from app.contexts.order.entities.order_item import OrderItem
from app.contexts.order.repositories.order_repository import OrderRepository
from app.contexts.order.schemas.order_schemas import (
    CustomerRequest,
    CustomerSummary,
    OrderItemRequest,
    OrderItemResponse,
    PendingOrderResponse,
)
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.shared.exceptions import BusinessRuleViolationError, ResourceNotFoundError


class OrderService:
    def __init__(self, order_repository: OrderRepository, menu_repository: MenuRepository):
        self._order_repo = order_repository
        self._menu_repo = menu_repository

    def submit_order(
        self,
        customer_data: CustomerRequest,
        items: list[OrderItemRequest],
    ) -> PendingOrderResponse:
        menu_items = self._validate_and_collect_menu_items(items)
        customer = self._find_or_create_customer(customer_data)
        order = self._order_repo.save_order(customer.id)
        order_items = self._build_and_save_order_items(order.id, items, menu_items)

        return PendingOrderResponse(
            order_id=order.id,
            status=order.status,
            customer=CustomerSummary(name=customer.name, phone_number=customer.phone_number),
            items=[
                OrderItemResponse(
                    menu_item_id=oi.menu_item_id,
                    name=menu_items[oi.menu_item_id].name,
                    base_selected=oi.base_selected,
                    toppings_selected=oi.toppings_selected,
                    quantity=oi.quantity,
                    unit_price=oi.unit_price,
                )
                for oi in order_items
            ],
            created_at=order.created_at,
        )

    def _validate_and_collect_menu_items(self, items: list[OrderItemRequest]) -> dict:
        menu_items = {}
        for item in items:
            menu_item = self._menu_repo.get_by_id(item.menu_item_id)

            if menu_item is None:
                raise ResourceNotFoundError(
                    message=f"Menu item {item.menu_item_id} does not exist",
                    detail=f"menu_item_id: {item.menu_item_id}",
                )
            if not menu_item.is_available:
                raise BusinessRuleViolationError(
                    message=f"'{menu_item.name}' is not currently available",
                    detail=f"menu_item_id: {item.menu_item_id}",
                )
            if item.base_selected not in menu_item.available_bases:
                raise BusinessRuleViolationError(
                    message=f"Base '{item.base_selected}' is not available for '{menu_item.name}'",
                    detail=f"base_selected: {item.base_selected}",
                )
            for topping in item.toppings_selected:
                if topping not in menu_item.available_toppings:
                    raise BusinessRuleViolationError(
                        message=f"Topping '{topping}' is not available for '{menu_item.name}'",
                        detail=f"toppings_selected: {topping}",
                    )

            menu_items[item.menu_item_id] = menu_item

        return menu_items

    def _find_or_create_customer(self, customer_data: CustomerRequest):
        customer = self._order_repo.find_customer_by_phone(customer_data.phone_number)
        if customer is None:
            customer = self._order_repo.save_customer(customer_data)
        return customer

    def _build_and_save_order_items(self, order_id: int, items: list[OrderItemRequest], menu_items: dict) -> list[OrderItem]:
        order_items = [
            OrderItem(
                order_id=order_id,
                menu_item_id=item.menu_item_id,
                base_selected=item.base_selected,
                toppings_selected=item.toppings_selected,
                quantity=item.quantity,
                unit_price=menu_items[item.menu_item_id].price,
            )
            for item in items
        ]
        return self._order_repo.save_order_items(order_items)
