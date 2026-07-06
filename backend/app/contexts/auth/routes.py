from fastapi import APIRouter

from app.contexts.auth.schemas.auth_schemas import LoginRequest, TokenResponse
from app.contexts.auth.service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    return AuthService().login(request)
