from typing import Optional
from pydantic import BaseModel, HttpUrl, ValidationError


class User(BaseModel):
    id: int
    email: str
    avatar: Optional[HttpUrl]


class ApiResponse(BaseModel):
    success: bool
    data: Optional[User]
    error: Optional[str]


def validate_user(payload: dict) -> Optional[User]:
    """Validate raw payload into a User model.
    Args:
        payload (dict): Raw data received from an external API."""
    try:
        user = User.model_validate(payload)
        return user
    except ValidationError:
        return None


def build_response(
        user: Optional[User], error_message: Optional[str]) -> ApiResponse:
    """Build a stable tool response contract.
    Args:
        user (Optional[User]): Validated user model.
        error_message (Optional[str]): Error message for failed validation."""
    is_success = user is not None and error_message is None
    response = ApiResponse(success=is_success, data=user, error=error_message)
    return response


def parse_payload(payload: dict) -> ApiResponse:
    """Parse external payload and return a tool response contract.
    Args:
        payload (dict): Raw data received from an external API."""
    try:
        user = User.model_validate(payload)
        response = build_response(user, None)
        return response
    except ValidationError as exc:
        response = build_response(None, str(exc))
        return response


if __name__ == '__main__':
    valid_payload = {
        'id': 1, 'email': 'test@example.com',
        'avatar': 'https://example.com/a.png'}

    invalid_payload = {
        'id': 'abc', 'email': 'test@example.com',
        'avatar': 'not-a-url'}

    valid_result = parse_payload(valid_payload)
    invalid_result = parse_payload(invalid_payload)

    print(f'\n[valid_result  ]: {valid_result.model_dump()}')
    print(f'\n[invalid_result]: {invalid_result.model_dump()}')
