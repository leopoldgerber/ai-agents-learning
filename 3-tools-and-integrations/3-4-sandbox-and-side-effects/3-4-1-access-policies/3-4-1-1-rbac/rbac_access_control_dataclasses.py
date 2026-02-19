from dataclasses import dataclass
from typing import Dict, List, Tuple


Permission = Tuple[str, str]  # (tool_name, action)


@dataclass(frozen=True)
class User:
    username: str
    role: str


@dataclass(frozen=True)
class Tool:
    name: str
    action: str


class RBACAccessControl:
    """
    Role-Based Access Control implementation.
    Principle: deny-by-default.
    """

    def __init__(self, permissions: Dict[str, List[Permission]]) -> None:
        self._permissions = permissions

    def can_access(self, user: User, tool: Tool) -> bool:
        """
        Check whether user role allows specific tool action.
        If role or permission not found -> access denied.
        """
        role_permissions = self._permissions.get(user.role, [])
        return (tool.name, tool.action) in role_permissions


def build_default_policy() -> RBACAccessControl:
    """Create default RBAC policy for agent tools."""
    permissions: Dict[str, List[Permission]] = {
        "admin": [
            ("database", "read"),
            ("database", "write"),
            ("database", "delete"),
            ("filesystem", "read"),
            ("filesystem", "write"),
            ("http_client", "execute"),
        ],
        "developer": [
            ("database", "read"),
            ("database", "write"),
            ("filesystem", "read"),
            ("http_client", "execute"),
        ],
        "analyst": [
            ("database", "read"),
            ("http_client", "execute"),
        ],
        "viewer": [
            ("database", "read"),
        ],
    }
    return RBACAccessControl(permissions=permissions)


def main() -> None:
    policy = build_default_policy()

    admin = User(username="alice", role="admin")
    viewer = User(username="bob", role="viewer")
    unknown = User(username="charlie", role="guest")

    tool_delete = Tool(name="database", action="delete")
    tool_read = Tool(name="database", action="read")

    print("admin delete:", policy.can_access(admin, tool_delete))
    print("viewer delete:", policy.can_access(viewer, tool_delete))
    print("viewer read:", policy.can_access(viewer, tool_read))
    print("guest read:", policy.can_access(unknown, tool_read))


if __name__ == "__main__":
    main()
