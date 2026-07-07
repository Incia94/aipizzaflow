from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.contexts.ai_advisor.router import router as ai_advisor_router
from app.contexts.analytics.router import router as analytics_router
from app.contexts.auth.router import router as auth_router
from app.contexts.checkout.router import router as checkout_router
from app.contexts.order.router import router as order_router
from app.contexts.reference.router import router as reference_router
from app.shared.config import settings
from app.shared.database import Base, engine, verify_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    verify_connection()
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(reference_router, prefix="/api/menu", tags=["Menu"])
app.include_router(order_router, prefix="/api/orders", tags=["Orders"])
app.include_router(checkout_router, prefix="/api/checkout", tags=["Checkout"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(ai_advisor_router, prefix="/api/ai", tags=["AI Advisor"])
