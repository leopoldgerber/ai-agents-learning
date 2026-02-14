class User:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role


class Tool:
    def __init__(self, name: str, action: str):
        self.name = name  # e.g. 'database', 'filesystem', 'http_client'
        self.action = action  # e.g. 'read', 'write', 'delete', 'execute'


class AccessControl:
    def __init__(self):
        # Define permissions for each role
        # Format: role -> list of allowed (tool, action) tuples
        self.permissions = {
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
            "analyst": [("database", "read"), ("http_client", "execute")],
            "viewer": [("database", "read")],
        }

    def can_access(self, user: User, tool: Tool) -> bool:
        """
        Checks whether the user is allowed to use the specified tool.

        Principle: deny-by-default — if no explicit permission is found,
        access is denied.
        """
        allowed_permissions = self.permissions.get(user.role, [])
        return (tool.name, tool.action) in allowed_permissions


# Usage example
user_admin = User("Alice", "admin")
user_viewer = User("Bob", "viewer")

tool_delete = Tool("database", "delete")
tool_read = Tool("database", "read")

ac = AccessControl()

print("Can admin delete? - ", ac.can_access(user_admin, tool_delete))
print("Viewer cannot delete? - ", ac.can_access(user_viewer, tool_delete))
print("Can viewer read? - ", ac.can_access(user_viewer, tool_read))

user_unknown = User("Charlie", "guest")
print(
    "Attempt with unknown role. - ", ac.can_access(user_unknown, tool_read)
)  # False - deny-by-default
