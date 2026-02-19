from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class User:
    username: str
    attributes: Dict[str, str]


@dataclass(frozen=True)
class Tool:
    name: str
    action: str
    attributes: Dict[str, str]


@dataclass(frozen=True)
class Context:
    environment: str  # dev / staging / production
    hour: int


class ABACPolicy:
    """
    Attribute-Based Access Control.
    Principle: deny-by-default.
    """

    def evaluate(
        self,
        user: User,
        tool: Tool,
        context: Context,
    ) -> Tuple[bool, str]:
        """Return (allowed, reason)."""

        if user.attributes.get("role") == "admin":
            return True, "Admin override"

        if context.environment == "production" and tool.action == "delete":
            return False, "Delete forbidden in production"

        if tool.attributes.get("sensitivity") == "high":
            if user.attributes.get("clearance") != "high":
                return False, "High sensitivity requires high clearance"

        if tool.name == "database" and tool.action in {"write", "delete"}:
            if not (9 <= context.hour <= 18):
                return False, "Database write/delete allowed 9-18 only"

        if tool.name == "filesystem":
            if user.attributes.get("department") != "engineering":
                return False, "Filesystem limited to engineering"
            if tool.action == "write" and context.environment != "dev":
                return False, "Filesystem write only in dev"

        if tool.name == "http_client":
            if user.attributes.get("clearance") not in {"medium", "high"}:
                return False, "HTTP requires clearance >= medium"

        if tool.action == "read":
            return True, "Read allowed"

        return False, "Denied by default"


def main() -> None:
    policy = ABACPolicy()

    user = User(
        username="alice",
        attributes={
            "role": "developer",
            "department": "engineering",
            "clearance": "high",
        },
    )

    tool = Tool(
        name="database",
        action="delete",
        attributes={"sensitivity": "high"},
    )

    context = Context(environment="production", hour=14)

    allowed, reason = policy.evaluate(user, tool, context)
    print("allowed:", allowed)
    print("reason:", reason)


if __name__ == "__main__":
    main()
