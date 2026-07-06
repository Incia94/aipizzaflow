from app.contexts.checkout.repositories.checkout_repository import CheckoutRepository
from app.contexts.checkout.schemas.checkout_schemas import (
    BillResponse,
    CompleteCheckoutResponse,
)
from app.shared.exceptions import BusinessRuleViolationError, ResourceNotFoundError

GST_RATE = 18.0


class CheckoutService:
    def __init__(self, repository: CheckoutRepository):
        self._repo = repository

    def complete_checkout(
        self, pending_order_id: int, payment_method: str
    ) -> CompleteCheckoutResponse:
        order = self._repo.get_pending_order(pending_order_id)
        if order is None:
            raise ResourceNotFoundError(
                message=f"No pending order found with ID {pending_order_id}",
                detail=f"pending_order_id: {pending_order_id}",
            )

        order_items = self._repo.get_order_items(pending_order_id)
        if not order_items:
            raise BusinessRuleViolationError(
                message="Order has no items and cannot be checked out",
                detail=f"order_id: {pending_order_id}",
            )

        subtotal = sum(item.unit_price * item.quantity for item in order_items)
        gst_amount = round(subtotal * GST_RATE / 100, 2)
        total_amount = round(subtotal + gst_amount, 2)

        order, bill, payment = self._repo.complete_transaction(
            order=order,
            subtotal=subtotal,
            gst_rate=GST_RATE,
            gst_amount=gst_amount,
            total_amount=total_amount,
            payment_method=payment_method,
        )

        return CompleteCheckoutResponse(
            order_id=order.id,
            status=order.status,
            bill=BillResponse(
                subtotal=bill.subtotal,
                gst_rate=bill.gst_rate,
                gst_amount=bill.gst_amount,
                total_amount=bill.total_amount,
            ),
            payment_method=payment.payment_method,
            paid_at=payment.created_at,
        )
