import json
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, ValidationError


class ToolCallSchema(BaseModel):
    """Strict schema for tool invocation."""

    tool_name: str
    user_id: int
    action: str


@dataclass(frozen=True)
class ParseResult:
    success: bool
    data: Optional[ToolCallSchema]
    error: Optional[str]


def parse_model_output(
    raw_output: str,
) -> ParseResult:
    """
    Parse model output as strict JSON tool call.
    """

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        return ParseResult(False, None, "Invalid JSON")

    try:
        validated = ToolCallSchema.model_validate(data)
    except ValidationError as exc:
        return ParseResult(False, None, f"Schema validation failed: {exc}")

    return ParseResult(True, validated, None)


def main() -> None:
    valid_output = """
    {
        "tool_name": "database",
        "user_id": 42,
        "action": "read"
    }
    """

    invalid_output = """
    {
        "tool_name": "database",
        "user_id": "not_int",
        "action": "read"
    }
    """

    print("valid:", parse_model_output(valid_output))
    print("\ninvalid:", parse_model_output(invalid_output))


if __name__ == "__main__":
    main()
