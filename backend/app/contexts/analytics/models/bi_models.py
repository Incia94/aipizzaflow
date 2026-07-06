from pydantic import BaseModel


class RevenueMetrics(BaseModel):
    total_revenue: float = 0.0
    total_gst_collected: float = 0.0
    average_order_value: float = 0.0


class SalesMetrics(BaseModel):
    total_orders: int = 0
    total_items_sold: int = 0
    average_items_per_order: float = 0.0


class CustomerMetrics(BaseModel):
    total_customers: int = 0
    new_customers: int = 0
    returning_customers: int = 0


class ProductMetrics(BaseModel):
    top_selling_items: dict[str, int] = {}
    revenue_by_category: dict[str, float] = {}
    most_popular_base: str = ""


class PaymentMetrics(BaseModel):
    revenue_by_payment_method: dict[str, float] = {}
    orders_by_payment_method: dict[str, int] = {}


class GrowthMetrics(BaseModel):
    week_over_week_revenue_change: float = 0.0
    month_over_month_revenue_change: float = 0.0


class BusinessIntelligenceModel(BaseModel):
    revenue: RevenueMetrics = RevenueMetrics()
    sales: SalesMetrics = SalesMetrics()
    customers: CustomerMetrics = CustomerMetrics()
    products: ProductMetrics = ProductMetrics()
    payments: PaymentMetrics = PaymentMetrics()
    growth: GrowthMetrics = GrowthMetrics()
