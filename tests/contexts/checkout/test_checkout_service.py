from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.contexts.checkout.entities.bill import Bill
from app.contexts.checkout.entities.payment import Payment
from app.contexts.checkout.repositories.checkout_repository import CheckoutRepository
from app.contexts.checkout.schemas.checkout_schemas import CompleteCheckoutResponse
from app.contexts.checkout.service import CheckoutService, GST_RATE
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem
from app.shared.exceptions import BusinessRuleViolationError, ResourceNotFoundError


@pytest.fixture
def mock_repo() -> CheckoutRepository:
    return MagicMock(spec=CheckoutRepository)


@pytest.fixture
def service(mock_repo) -> CheckoutService:
    return CheckoutService(repository=mock_repo)


@pytest.fixture
def pending_order() -> Order:
    return Order(id=10, customer_id=1, status="pending", created_at=datetime.utcnow(), updated_at=datetime.utcnow())


@pytest.fixture
def order_items() -> list[OrderItem]:
    return [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=[], quantity=2, unit_price=299.0),
    ]


@pytest.fixture
def completed_bill() -> Bill:
    return Bill(id=1, order_id=10, subtotal=598.0, gst_rate=18.0,
                gst_amount=107.64, total_amount=705.64, created_at=datetime.utcnow())


@pytest.fixture
def completed_payment() -> Payment:
    return Payment(id=1, order_id=10, bill_id=1, payment_method="card",
                   amount_paid=705.64, created_at=datetime.utcnow())


def _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment):
    paid_order = Order(id=10, customer_id=1, status="paid",
                       created_at=pending_order.created_at, updated_at=datetime.utcnow())
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = order_items
    mock_repo.complete_transaction.return_value = (paid_order, completed_bill, completed_payment)


def test_complete_checkout_returns_response(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    result = service.complete_checkout(10, "card")

    assert isinstance(result, CompleteCheckoutResponse)
    assert result.order_id == 10
    assert result.status == "paid"
    assert result.payment_method == "card"


def test_complete_checkout_calculates_gst_at_18_percent(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    service.complete_checkout(10, "card")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["gst_rate"] == 18.0
    assert call_kwargs["subtotal"] == 598.0
    assert call_kwargs["gst_amount"] == 107.64
    assert call_kwargs["total_amount"] == 705.64


def test_complete_checkout_captures_gst_rate_at_transaction_time(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    service.complete_checkout(10, "cash")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["gst_rate"] == GST_RATE


def test_complete_checkout_calculates_subtotal_from_unit_price_times_quantity(service, mock_repo, pending_order, completed_bill, completed_payment):
    items = [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=[], quantity=3, unit_price=399.0),
    ]
    paid_order = Order(id=10, customer_id=1, status="paid",
                       created_at=pending_order.created_at, updated_at=datetime.utcnow())
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = items
    mock_repo.complete_transaction.return_value = (paid_order, completed_bill, completed_payment)

    service.complete_checkout(10, "upi")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["subtotal"] == 1197.0  # 3 × 399.0


def test_complete_checkout_raises_resource_not_found_for_unknown_order(service, mock_repo):
    mock_repo.get_pending_order.return_value = None

    with pytest.raises(ResourceNotFoundError) as exc:
        service.complete_checkout(99999, "cash")

    assert "99999" in exc.value.message


def test_complete_checkout_raises_when_order_has_no_items(service, mock_repo, pending_order):
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = []

    with pytest.raises(BusinessRuleViolationError):
        service.complete_checkout(10, "cash")


def test_complete_checkout_passes_payment_method_to_repository(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    service.complete_checkout(10, "upi")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["payment_method"] == "upi"


def test_complete_checkout_bill_fields_in_response(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    result = service.complete_checkout(10, "card")

    assert result.bill.subtotal == 598.0
    assert result.bill.gst_rate == 18.0
    assert result.bill.gst_amount == 107.64
    assert result.bill.total_amount == 705.64
