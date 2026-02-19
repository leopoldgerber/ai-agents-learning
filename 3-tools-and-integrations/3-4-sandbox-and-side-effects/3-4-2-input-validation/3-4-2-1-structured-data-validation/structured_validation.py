import json
from typing import List
from pydantic import BaseModel, Field, ValidationError


class BookResult(BaseModel):
    """Validated schema for book search result."""

    title: str = Field(min_length=1, max_length=500)
    year: int = Field(ge=1000, le=2100)
    authors: List[str] = Field(min_length=1)


def parse_json_string(raw: str) -> dict:
    """
    Safely parse JSON string.
    Raises ValueError if invalid JSON.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON input") from exc


def validate_book(data: dict) -> BookResult:
    """
    Validate structured data using strict schema.
    """
    try:
        return BookResult.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"Schema validation failed: {exc}") from exc


def normalize_text(text: str, max_len: int = 5000) -> str:
    """
    Normalize whitespace and enforce max length.
    """
    clean = " ".join(text.split())
    if len(clean) > max_len:
        clean = clean[:max_len] + "... [truncated]"
    return clean


def main() -> None:
    raw_json = """
    {
        "title": "Clean Code",
        "year": 2008,
        "authors": ["Robert C. Martin"]
    }
    """

    data = parse_json_string(raw_json)
    validated = validate_book(data)

    validated.title = normalize_text(validated.title)

    print(validated.model_dump())


if __name__ == "__main__":
    main()
