"""
RFC 7807 Problem Details Error Handling for QSCI API.

All API errors are returned as application/problem+json with
a structured, machine-readable payload.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class ProblemDetails(BaseModel):
    """RFC 7807 Problem Details payload."""
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
    invalid_params: Optional[List[Dict[str, Any]]] = None


class ProblemDetailsException(Exception):
    """Raise this from any endpoint to return a structured RFC 7807 error."""
    def __init__(
        self,
        status_code: int,
        title: str,
        detail: str,
        type_uri: str = "about:blank",
        instance: Optional[str] = None,
        invalid_params: Optional[List[Dict[str, Any]]] = None,
    ):
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.type_uri = type_uri
        self.instance = instance
        self.invalid_params = invalid_params


# Convenience factory functions
def not_found(entity: str, entity_id: str) -> ProblemDetailsException:
    return ProblemDetailsException(
        status_code=404,
        title=f"{entity} Not Found",
        detail=f"{entity} with id '{entity_id}' does not exist.",
        type_uri="/errors/not-found",
    )


def forbidden(detail: str = "You do not have permission to perform this action.") -> ProblemDetailsException:
    return ProblemDetailsException(
        status_code=403,
        title="Forbidden",
        detail=detail,
        type_uri="/errors/forbidden",
    )


def conflict(detail: str) -> ProblemDetailsException:
    return ProblemDetailsException(
        status_code=409,
        title="Conflict",
        detail=detail,
        type_uri="/errors/conflict",
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register the global RFC 7807 exception handler on the FastAPI app."""
    @app.exception_handler(ProblemDetailsException)
    async def problem_details_handler(request: Request, exc: ProblemDetailsException):
        payload = ProblemDetails(
            type=exc.type_uri,
            title=exc.title,
            status=exc.status_code,
            detail=exc.detail,
            instance=exc.instance or str(request.url),
            invalid_params=exc.invalid_params,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=payload.model_dump(exclude_none=True),
            media_type="application/problem+json",
        )
