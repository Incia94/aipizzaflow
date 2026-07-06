from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contexts.analytics.repositories.analytics_repository import AnalyticsRepository
from app.contexts.analytics.schemas.analytics_schemas import AnalyticsRequest, AnalyticsResponse
from app.contexts.analytics.service import AnalyticsService
from app.contexts.auth.dependencies import get_current_admin
from app.shared.database import get_db

router = APIRouter(dependencies=[Depends(get_current_admin)])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(db))


@router.get("", response_model=AnalyticsResponse)
def retrieve_business_intelligence(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    customer_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    pizza_id: Optional[int] = None,
    category: Optional[str] = None,
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsResponse:
    filters = AnalyticsRequest(
        from_date=from_date,
        to_date=to_date,
        customer_id=customer_id,
        payment_method=payment_method,
        pizza_id=pizza_id,
        category=category,
    )
    return service.retrieve_business_intelligence(filters)
