import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError


app = FastAPI()

logger = logging.getLogger('uvicorn.error')


class UserInput(BaseModel):
    """Validated user input payload.
    Args:
        None: No args."""
    model_config = ConfigDict(extra='forbid')

    user_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=80)
    email: str | None = Field(default=None, min_length=3, max_length=254)


class UserResponse(BaseModel):
    """Validated response payload.
    Args:
        None: No args."""
    status: str
    user: UserInput


class ErrorResponse(BaseModel):
    """Validation error response payload.
    Args:
        None: No args."""
    status: str
    errors: list[dict[str, Any]]


def validate_payload(payload: dict[str, Any]) -> UserInput:
    """Validate raw payload using Pydantic model.
    Args:
        payload (dict[str, Any]): Raw JSON object from client."""
    return UserInput.model_validate(payload)


def build_error(errors: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a minimal error response.
    Args:
        errors (list[dict[str, Any]]): Pydantic validation errors."""
    return {'status': 'error', 'errors': errors}


@app.get('/health')
async def health() -> dict[str, bool]:
    """Health check endpoint.
    Args:
        None: No args."""
    return {'ok': True}


@app.post(
    '/validate',
    response_model=UserResponse,
    responses={400: {'model': ErrorResponse}},
)
async def validate_user(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate input JSON via Pydantic and return typed response.
    Args:
        payload (dict[str, Any]): Raw JSON payload."""
    try:
        user = validate_payload(payload=payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=build_error(errors=exc.errors()),
        )

    return {'status': 'ok', 'user': user}
