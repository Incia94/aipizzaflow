from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.contexts.ai_advisor.llm_client import LLMClient
from app.contexts.ai_advisor.schemas.ai_advisor_schemas import AIQueryRequest, AIQueryResponse
from app.contexts.ai_advisor.service import AIService
from app.contexts.analytics.models.bi_models import (
    BusinessIntelligenceModel,
    CustomerMetrics,
    GrowthMetrics,
    PaymentMetrics,
    ProductMetrics,
    RevenueMetrics,
    SalesMetrics,
)
from app.contexts.analytics.schemas.analytics_schemas import AnalyticsRequest, AnalyticsResponse
from app.contexts.analytics.service import AnalyticsService


@pytest.fixture
def mock_analytics() -> AnalyticsService:
    return MagicMock(spec=AnalyticsService)


@pytest.fixture
def mock_llm() -> LLMClient:
    return MagicMock(spec=LLMClient)


@pytest.fixture
def service(mock_analytics, mock_llm) -> AIService:
    return AIService(analytics_service=mock_analytics, llm_client=mock_llm)


@pytest.fixture
def sample_bi() -> BusinessIntelligenceModel:
    return BusinessIntelligenceModel(
        revenue=RevenueMetrics(total_revenue=705.64, total_gst_collected=107.64, average_order_value=705.64),
        sales=SalesMetrics(total_orders=1, total_items_sold=2, average_items_per_order=2.0),
        customers=CustomerMetrics(total_customers=1, new_customers=1, returning_customers=0),
        products=ProductMetrics(top_selling_items={"1": 2}, revenue_by_category={}, most_popular_base="Thin Crust"),
        payments=PaymentMetrics(revenue_by_payment_method={"card": 705.64}, orders_by_payment_method={"card": 1}),
        growth=GrowthMetrics(week_over_week_revenue_change=0.0, month_over_month_revenue_change=0.0),
    )


def _setup(mock_analytics, mock_llm, sample_bi, llm_answer="Looks good."):
    mock_analytics.retrieve_business_intelligence.return_value = AnalyticsResponse(
        filters_applied=AnalyticsRequest(),
        intelligence=sample_bi,
    )
    mock_llm.complete.return_value = llm_answer


def test_query_returns_ai_query_response(service, mock_analytics, mock_llm, sample_bi):
    _setup(mock_analytics, mock_llm, sample_bi)

    result = service.query(AIQueryRequest(question="How are sales?"))

    assert isinstance(result, AIQueryResponse)


def test_query_echoes_question_in_response(service, mock_analytics, mock_llm, sample_bi):
    _setup(mock_analytics, mock_llm, sample_bi)

    result = service.query(AIQueryRequest(question="What is my best-selling pizza?"))

    assert result.question == "What is my best-selling pizza?"


def test_query_returns_llm_answer(service, mock_analytics, mock_llm, sample_bi):
    _setup(mock_analytics, mock_llm, sample_bi, llm_answer="Your best seller is Margherita.")

    result = service.query(AIQueryRequest(question="Best pizza?"))

    assert result.answer == "Your best seller is Margherita."


def test_query_includes_intelligence_snapshot(service, mock_analytics, mock_llm, sample_bi):
    _setup(mock_analytics, mock_llm, sample_bi)

    result = service.query(AIQueryRequest(question="Revenue?"))

    assert result.intelligence_snapshot.revenue.total_revenue == 705.64


def test_query_calls_analytics_service_with_provided_filters(service, mock_analytics, mock_llm, sample_bi):
    _setup(mock_analytics, mock_llm, sample_bi)
    filters = AnalyticsRequest(payment_method="card")

    service.query(AIQueryRequest(question="Card revenue?", filters=filters))

    mock_analytics.retrieve_business_intelligence.assert_called_once_with(filters)


def test_query_calls_analytics_service_with_empty_filters_when_none_provided(service, mock_analytics, mock_llm, sample_bi):
    _setup(mock_analytics, mock_llm, sample_bi)

    service.query(AIQueryRequest(question="Overview?"))

    call_args = mock_analytics.retrieve_business_intelligence.call_args
    assert call_args[0][0] == AnalyticsRequest()


def test_query_passes_system_prompt_and_user_message_to_llm(service, mock_analytics, mock_llm, sample_bi):
    _setup(mock_analytics, mock_llm, sample_bi)

    service.query(AIQueryRequest(question="How are sales?"))

    mock_llm.complete.assert_called_once()
    call_kwargs = mock_llm.complete.call_args
    system_prompt = call_kwargs[1]["system_prompt"] if "system_prompt" in call_kwargs[1] else call_kwargs[0][0]
    user_message = call_kwargs[1]["user_message"] if "user_message" in call_kwargs[1] else call_kwargs[0][1]
    assert "pizza" in system_prompt.lower()
    assert "How are sales?" in user_message


def test_query_includes_revenue_data_in_llm_message(service, mock_analytics, mock_llm, sample_bi):
    _setup(mock_analytics, mock_llm, sample_bi)

    service.query(AIQueryRequest(question="Revenue?"))

    _, kwargs = mock_llm.complete.call_args
    user_message = kwargs.get("user_message") or mock_llm.complete.call_args[0][1]
    assert "705.64" in user_message


def test_query_ai_service_never_performs_calculations(service, mock_analytics, mock_llm, sample_bi):
    """AIService must not compute BI metrics — it only passes the analytics result to the LLM."""
    _setup(mock_analytics, mock_llm, sample_bi)

    service.query(AIQueryRequest(question="Analysis?"))

    mock_analytics.retrieve_business_intelligence.assert_called_once()
    mock_llm.complete.assert_called_once()
