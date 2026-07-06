from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ApplicationError(Exception):
    def __init__(self, message: str, detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class InvalidInputError(ApplicationError):
    pass


class BusinessRuleViolationError(ApplicationError):
    pass


class ResourceNotFoundError(ApplicationError):
    pass


class ExternalServiceError(ApplicationError):
    pass


class UnexpectedSystemError(ApplicationError):
    pass


def _error_body(category: str, exc: ApplicationError) -> dict:
    body: dict = {"error": category, "message": exc.message}
    if exc.detail:
        body["detail"] = exc.detail
    return body


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidInputError)
    async def handle_invalid_input(request: Request, exc: InvalidInputError) -> JSONResponse:
        return JSONResponse(status_code=400, content=_error_body("invalid_input", exc))

    @app.exception_handler(BusinessRuleViolationError)
    async def handle_business_rule_violation(request: Request, exc: BusinessRuleViolationError) -> JSONResponse:
        return JSONResponse(status_code=409, content=_error_body("business_rule_violation", exc))

    @app.exception_handler(ResourceNotFoundError)
    async def handle_resource_not_found(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content=_error_body("resource_not_found", exc))

    @app.exception_handler(ExternalServiceError)
    async def handle_external_service_error(request: Request, exc: ExternalServiceError) -> JSONResponse:
        return JSONResponse(status_code=503, content=_error_body("external_service_error", exc))

    @app.exception_handler(UnexpectedSystemError)
    async def handle_unexpected_system_error(request: Request, exc: UnexpectedSystemError) -> JSONResponse:
        return JSONResponse(status_code=500, content=_error_body("unexpected_system_error", exc))
