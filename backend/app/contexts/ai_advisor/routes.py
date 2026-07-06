from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contexts.ai_advisor.openrouter_client import OpenRouterClient
from app.contexts.ai_advisor.schemas.ai_advisor_schemas import AIQueryRequest, AIQueryResponse
from app.contexts.ai_advisor.service import AIService
from app.contexts.analytics.repositories.analytics_repository import AnalyticsRepository
from app.contexts.analytics.service import AnalyticsService
from app.contexts.auth.dependencies import get_current_admin
from app.shared.database import get_db

router = APIRouter(dependencies=[Depends(get_current_admin)])


def get_ai_service(db: Session = Depends(get_db)) -> AIService:
    analytics_service = AnalyticsService(AnalyticsRepository(db))
    return AIService(analytics_service=analytics_service, llm_client=OpenRouterClient())


@router.post("/query", response_model=AIQueryResponse)
def query_advisor(
    request: AIQueryRequest,
    service: AIService = Depends(get_ai_service),
) -> AIQueryResponse:
    return service.query(request)
