from collections import Counter, defaultdict
from datetime import datetime, timedelta

from app.contexts.analytics.models.bi_models import (
    BusinessIntelligenceModel,
    CustomerMetrics,
    GrowthMetrics,
    PaymentMetrics,
    ProductMetrics,
    RevenueMetrics,
    SalesMetrics,
)
from app.contexts.analytics.repositories.analytics_repository import AnalyticsRepository
from app.contexts.analytics.schemas.analytics_schemas import AnalyticsRequest, AnalyticsResponse
from app.contexts.checkout.entities.bill import Bill
from app.contexts.checkout.entities.payment import Payment
from app.contexts.order.entities.customer import Customer
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem
from app.contexts.reference.entities.menu_item import MenuItem


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository):
        self._repository = repository

    def retrieve_business_intelligence(self, filters: AnalyticsRequest) -> AnalyticsResponse:
        orders = self._repository.get_paid_orders(filters)
        order_ids = [o.id for o in orders]
        customer_ids = list({o.customer_id for o in orders})

        items = self._repository.get_order_items(order_ids)
        bills = self._repository.get_bills(order_ids)
        customers = self._repository.get_customers(customer_ids)
        payments = self._repository.get_payments(order_ids)

        intelligence = BusinessIntelligenceModel(
            revenue=self._compute_revenue(bills),
            sales=self._compute_sales(orders, items),
            customers=self._compute_customers(customers, orders),
            products=self._compute_products(items),
            payments=self._compute_payments(payments),
            growth=self._compute_growth(filters),
        )
        return AnalyticsResponse(filters_applied=filters, intelligence=intelligence)

    def _compute_revenue(self, bills: list[Bill]) -> RevenueMetrics:
        if not bills:
            return RevenueMetrics()
        total_revenue = round(sum(b.total_amount for b in bills), 2)
        total_gst = round(sum(b.gst_amount for b in bills), 2)
        avg_order_value = round(total_revenue / len(bills), 2)
        return RevenueMetrics(
            total_revenue=total_revenue,
            total_gst_collected=total_gst,
            average_order_value=avg_order_value,
        )

    def _compute_sales(self, orders: list[Order], items: list[OrderItem]) -> SalesMetrics:
        total_orders = len(orders)
        total_items = sum(i.quantity for i in items)
        avg_items = round(total_items / total_orders, 2) if total_orders else 0.0
        return SalesMetrics(
            total_orders=total_orders,
            total_items_sold=total_items,
            average_items_per_order=avg_items,
        )

    def _compute_customers(self, customers: list[Customer], orders: list[Order]) -> CustomerMetrics:
        order_counts: Counter[int] = Counter(o.customer_id for o in orders)
        new_customers = sum(1 for cid, count in order_counts.items() if count == 1)
        returning_customers = sum(1 for cid, count in order_counts.items() if count > 1)
        return CustomerMetrics(
            total_customers=len(customers),
            new_customers=new_customers,
            returning_customers=returning_customers,
        )

    def _compute_products(self, items: list[OrderItem]) -> ProductMetrics:
        if not items:
            return ProductMetrics()

        item_counts: Counter[int] = Counter()
        item_names: dict[int, str] = {}
        category_revenue: defaultdict[str, float] = defaultdict(float)
        base_counts: Counter[str] = Counter()

        for item in items:
            item_counts[item.menu_item_id] += item.quantity
            base_counts[item.base_selected] += item.quantity

        top_ids = [menu_item_id for menu_item_id, _ in item_counts.most_common(5)]
        top_selling: dict[str, int] = {}
        for menu_item_id in top_ids:
            top_selling[str(menu_item_id)] = item_counts[menu_item_id]

        most_popular_base = base_counts.most_common(1)[0][0] if base_counts else ""

        return ProductMetrics(
            top_selling_items=top_selling,
            revenue_by_category=dict(category_revenue),
            most_popular_base=most_popular_base,
        )

    def _compute_payments(self, payments: list[Payment]) -> PaymentMetrics:
        revenue_by_method: defaultdict[str, float] = defaultdict(float)
        orders_by_method: defaultdict[str, int] = defaultdict(int)
        for p in payments:
            revenue_by_method[p.payment_method] = round(revenue_by_method[p.payment_method] + p.amount_paid, 2)
            orders_by_method[p.payment_method] += 1
        return PaymentMetrics(
            revenue_by_payment_method=dict(revenue_by_method),
            orders_by_payment_method=dict(orders_by_method),
        )

    def _compute_growth(self, filters: AnalyticsRequest) -> GrowthMetrics:
        today = datetime.utcnow().date()
        current_end = filters.to_date or today
        current_start = filters.from_date or (today - timedelta(days=30))

        period_length = (current_end - current_start).days or 1

        prev_end = current_start - timedelta(days=1)
        prev_start_week = current_end - timedelta(weeks=2)
        prev_start_month = current_start - timedelta(days=period_length)

        from app.contexts.analytics.schemas.analytics_schemas import AnalyticsRequest as AR

        current_orders = self._repository.get_paid_orders(
            AR(from_date=current_start, to_date=current_end)
        )
        current_bills = self._repository.get_bills([o.id for o in current_orders])
        current_revenue = sum(b.total_amount for b in current_bills)

        prev_week_orders = self._repository.get_paid_orders(
            AR(from_date=prev_start_week, to_date=prev_end)
        )
        prev_week_bills = self._repository.get_bills([o.id for o in prev_week_orders])
        prev_week_revenue = sum(b.total_amount for b in prev_week_bills)

        prev_month_orders = self._repository.get_paid_orders(
            AR(from_date=prev_start_month, to_date=prev_end)
        )
        prev_month_bills = self._repository.get_bills([o.id for o in prev_month_orders])
        prev_month_revenue = sum(b.total_amount for b in prev_month_bills)

        def pct_change(current: float, previous: float) -> float:
            if previous == 0:
                return 0.0
            return round((current - previous) / previous * 100, 2)

        return GrowthMetrics(
            week_over_week_revenue_change=pct_change(current_revenue, prev_week_revenue),
            month_over_month_revenue_change=pct_change(current_revenue, prev_month_revenue),
        )
