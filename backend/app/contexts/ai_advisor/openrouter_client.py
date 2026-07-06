import httpx

from app.shared.config import settings
from app.shared.exceptions import ExternalServiceError


class OpenRouterClient:
    def complete(self, system_prompt: str, user_message: str) -> str:
        payload = {
            "model": settings.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }
        try:
            response = httpx.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                message="OpenRouter request failed",
                detail=f"HTTP {exc.response.status_code}",
            ) from exc
        except (httpx.RequestError, KeyError, IndexError) as exc:
            raise ExternalServiceError(
                message="OpenRouter request failed",
                detail=str(exc),
            ) from exc
