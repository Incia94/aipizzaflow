from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.contexts.analytics.models.bi_models import BusinessIntelligenceModel


class AnalyticsRequest(BaseModel):
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    customer_id: Optional[int] = None
    payment_method: Optional[str] = None
    pizza_id: Optional[int] = None
    category: Optional[str] = None


class AnalyticsResponse(BaseModel):
    filters_applied: AnalyticsRequest
    intelligence: BusinessIntelligenceModel
