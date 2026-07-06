from app.contexts.ai_advisor.llm_client import LLMClient
from app.contexts.ai_advisor.schemas.ai_advisor_schemas import AIQueryRequest, AIQueryResponse
from app.contexts.analytics.models.bi_models import BusinessIntelligenceModel
from app.contexts.analytics.schemas.analytics_schemas import AnalyticsRequest
from app.contexts.analytics.service import AnalyticsService

_SYSTEM_PROMPT = """\
You are an AI business advisor for PizzaFlow, a pizza restaurant management system.
You analyze factual business intelligence data and provide the restaurant owner with
concise, specific, and actionable insights.

Rules:
- Base your answer exclusively on the business intelligence data provided.
- Be concise: 2-4 sentences maximum.
- Reference specific numbers when they support the insight.
- Do not speculate or invent information not present in the data.\
"""


def _format_bi_for_prompt(bi: BusinessIntelligenceModel) -> str:
    rev = bi.revenue
    sal = bi.sales
    cus = bi.customers
    pro = bi.products
    pay = bi.payments
    gro = bi.growth

    payment_lines = "\n".join(
        f"  - {method.title()}: ₹{amount:.2f} ({pay.orders_by_payment_method.get(method, 0)} orders)"
        for method, amount in pay.revenue_by_payment_method.items()
    ) or "  - No payment data"

    top_items_lines = "\n".join(
        f"  - Item #{item_id}: {qty} sold"
        for item_id, qty in list(bi.products.top_selling_items.items())[:3]
    ) or "  - No sales data"

    return f"""\
REVENUE
  Total Revenue:        ₹{rev.total_revenue:.2f}
  GST Collected:        ₹{rev.total_gst_collected:.2f}
  Avg Order Value:      ₹{rev.average_order_value:.2f}

SALES
  Total Orders:         {sal.total_orders}
  Total Items Sold:     {sal.total_items_sold}
  Avg Items/Order:      {sal.average_items_per_order}

CUSTOMERS
  Total Customers:      {cus.total_customers}
  New Customers:        {cus.new_customers}
  Returning Customers:  {cus.returning_customers}

TOP SELLING ITEMS
{top_items_lines}
  Most Popular Base:    {pro.most_popular_base or "N/A"}

PAYMENTS
{payment_lines}

GROWTH
  Week-over-Week:       {gro.week_over_week_revenue_change:+.1f}%
  Month-over-Month:     {gro.month_over_month_revenue_change:+.1f}%\
"""


class AIService:
    def __init__(self, analytics_service: AnalyticsService, llm_client: LLMClient):
        self._analytics = analytics_service
        self._llm = llm_client

    def query(self, request: AIQueryRequest) -> AIQueryResponse:
        filters = request.filters or AnalyticsRequest()
        analytics_response = self._analytics.retrieve_business_intelligence(filters)
        bi = analytics_response.intelligence

        user_message = (
            f"Business Intelligence Report:\n\n"
            f"{_format_bi_for_prompt(bi)}\n\n"
            f"Owner's Question: {request.question}"
        )

        answer = self._llm.complete(
            system_prompt=_SYSTEM_PROMPT,
            user_message=user_message,
        )

        return AIQueryResponse(
            question=request.question,
            answer=answer,
            intelligence_snapshot=bi,
        )
