from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.contexts.analytics.models.bi_models import BusinessIntelligenceModel
from app.contexts.analytics.repositories.analytics_repository import AnalyticsRepository
from app.contexts.analytics.schemas.analytics_schemas import AnalyticsRequest, AnalyticsResponse
from app.contexts.analytics.service import AnalyticsService
from app.contexts.checkout.entities.bill import Bill
from app.contexts.checkout.entities.payment import Payment
from app.contexts.order.entities.customer import Customer
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem


@pytest.fixture
def mock_repo() -> AnalyticsRepository:
    return MagicMock(spec=AnalyticsRepository)


@pytest.fixture
def service(mock_repo) -> AnalyticsService:
    return AnalyticsService(repository=mock_repo)


@pytest.fixture
def paid_orders() -> list[Order]:
    return [
        Order(id=1, customer_id=1, status="paid", created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        Order(id=2, customer_id=2, status="paid", created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
    ]


@pytest.fixture
def order_items() -> list[OrderItem]:
    return [
        OrderItem(id=1, order_id=1, menu_item_id=1, base_selected="Thin Crust", toppings_selected=[], quantity=2, unit_price=299.0),
        OrderItem(id=2, order_id=2, menu_item_id=2, base_selected="Thick Crust", toppings_selected=[], quantity=1, unit_price=399.0),
    ]


@pytest.fixture
def bills() -> list[Bill]:
    return [
        Bill(id=1, order_id=1, subtotal=598.0, gst_rate=18.0, gst_amount=107.64, total_amount=705.64, created_at=datetime.utcnow()),
        Bill(id=2, order_id=2, subtotal=399.0, gst_rate=18.0, gst_amount=71.82, total_amount=470.82, created_at=datetime.utcnow()),
    ]


@pytest.fixture
def customers() -> list[Customer]:
    return [
        Customer(id=1, name="Rajan", phone_number="9999999999", created_at=datetime.utcnow()),
        Customer(id=2, name="Priya", phone_number="8888888888", created_at=datetime.utcnow()),
    ]


@pytest.fixture
def payments() -> list[Payment]:
    return [
        Payment(id=1, order_id=1, bill_id=1, payment_method="card", amount_paid=705.64, created_at=datetime.utcnow()),
        Payment(id=2, order_id=2, bill_id=2, payment_method="cash", amount_paid=470.82, created_at=datetime.utcnow()),
    ]


def _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments):
    mock_repo.get_paid_orders.return_value = paid_orders
    mock_repo.get_order_items.return_value = order_items
    mock_repo.get_bills.return_value = bills
    mock_repo.get_customers.return_value = customers
    mock_repo.get_payments.return_value = payments


def test_retrieve_business_intelligence_returns_analytics_response(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    assert isinstance(result, AnalyticsResponse)
    assert isinstance(result.intelligence, BusinessIntelligenceModel)


def test_revenue_metrics_total_is_sum_of_bill_totals(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    assert result.intelligence.revenue.total_revenue == round(705.64 + 470.82, 2)


def test_revenue_metrics_gst_is_sum_of_bill_gst_amounts(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    assert result.intelligence.revenue.total_gst_collected == round(107.64 + 71.82, 2)


def test_revenue_metrics_average_order_value_is_computed(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    expected_avg = round((705.64 + 470.82) / 2, 2)
    assert result.intelligence.revenue.average_order_value == expected_avg


def test_sales_metrics_counts_total_orders(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    assert result.intelligence.sales.total_orders == 2


def test_sales_metrics_total_items_sums_quantities(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    assert result.intelligence.sales.total_items_sold == 3  # 2 + 1


def test_payment_metrics_groups_revenue_by_method(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    assert result.intelligence.payments.revenue_by_payment_method["card"] == 705.64
    assert result.intelligence.payments.revenue_by_payment_method["cash"] == 470.82


def test_payment_metrics_counts_orders_by_method(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    assert result.intelligence.payments.orders_by_payment_method["card"] == 1
    assert result.intelligence.payments.orders_by_payment_method["cash"] == 1


def test_customer_metrics_counts_unique_customers(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    assert result.intelligence.customers.total_customers == 2


def test_filters_applied_are_echoed_in_response(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)
    filters = AnalyticsRequest(payment_method="card")

    result = service.retrieve_business_intelligence(filters)

    assert result.filters_applied.payment_method == "card"


def test_empty_data_returns_zeroed_metrics(service, mock_repo):
    mock_repo.get_paid_orders.return_value = []
    mock_repo.get_order_items.return_value = []
    mock_repo.get_bills.return_value = []
    mock_repo.get_customers.return_value = []
    mock_repo.get_payments.return_value = []

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    assert result.intelligence.revenue.total_revenue == 0.0
    assert result.intelligence.sales.total_orders == 0
    assert result.intelligence.customers.total_customers == 0


def test_products_most_popular_base_is_computed(service, mock_repo, paid_orders, order_items, bills, customers, payments):
    _setup_mock(mock_repo, paid_orders, order_items, bills, customers, payments)

    result = service.retrieve_business_intelligence(AnalyticsRequest())

    assert result.intelligence.products.most_popular_base == "Thin Crust"
