from typing import Optional

from pydantic import BaseModel, Field

from app.contexts.analytics.models.bi_models import BusinessIntelligenceModel
from app.contexts.analytics.schemas.analytics_schemas import AnalyticsRequest


class AIQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    filters: Optional[AnalyticsRequest] = None


class AIQueryResponse(BaseModel):
    question: str
    answer: str
    intelligence_snapshot: BusinessIntelligenceModel
