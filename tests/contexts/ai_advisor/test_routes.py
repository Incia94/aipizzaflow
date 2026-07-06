import pytest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.contexts.ai_advisor.routes import get_ai_service
from app.contexts.ai_advisor.schemas.ai_advisor_schemas import AIQueryRequest, AIQueryResponse
from app.contexts.ai_advisor.service import AIService
from app.contexts.analytics.models.bi_models import BusinessIntelligenceModel
from app.contexts.auth.dependencies import get_current_admin
from app.main import app


@pytest.fixture
def mock_ai_service() -> AIService:
    service = MagicMock(spec=AIService)
    service.query.return_value = AIQueryResponse(
        question="How are sales?",
        answer="Sales are strong.",
        intelligence_snapshot=BusinessIntelligenceModel(),
    )
    return service


@pytest.fixture
def client_with_mock(mock_ai_service):
    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service
    app.dependency_overrides[get_current_admin] = lambda: "test-admin"
    yield TestClient(app, raise_server_exceptions=True)
    app.dependency_overrides.clear()


def test_query_returns_200(client_with_mock):
    response = client_with_mock.post("/ai/query", json={"question": "How are sales?"})

    assert response.status_code == 200


def test_query_response_has_answer_field(client_with_mock):
    response = client_with_mock.post("/ai/query", json={"question": "How are sales?"})

    assert "answer" in response.json()
    assert response.json()["answer"] == "Sales are strong."


def test_query_response_has_question_field(client_with_mock):
    response = client_with_mock.post("/ai/query", json={"question": "How are sales?"})

    assert response.json()["question"] == "How are sales?"


def test_query_response_has_intelligence_snapshot(client_with_mock):
    response = client_with_mock.post("/ai/query", json={"question": "How are sales?"})

    assert "intelligence_snapshot" in response.json()


def test_query_with_filters_passes_them_to_service(client_with_mock, mock_ai_service):
    client_with_mock.post("/ai/query", json={
        "question": "Card revenue?",
        "filters": {"payment_method": "card"},
    })

    mock_ai_service.query.assert_called_once()
    request_arg = mock_ai_service.query.call_args[0][0]
    assert request_arg.filters.payment_method == "card"


def test_query_missing_question_returns_422(client_with_mock):
    response = client_with_mock.post("/ai/query", json={})

    assert response.status_code == 422


def test_query_empty_question_returns_422(client_with_mock):
    response = client_with_mock.post("/ai/query", json={"question": ""})

    assert response.status_code == 422
