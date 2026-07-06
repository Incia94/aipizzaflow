from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt

from app.contexts.auth.schemas.auth_schemas import LoginRequest, TokenResponse
from app.shared.config import settings

_ALGORITHM = "HS256"
_EXPIRE_HOURS = 24


class AuthService:
    def login(self, request: LoginRequest) -> TokenResponse:
        if request.username != settings.admin_username or request.password != settings.admin_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = {
            "sub": request.username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=_EXPIRE_HOURS),
        }
        token = jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)
        return TokenResponse(access_token=token)
