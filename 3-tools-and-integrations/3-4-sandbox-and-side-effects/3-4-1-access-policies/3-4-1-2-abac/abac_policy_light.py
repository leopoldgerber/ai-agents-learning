class User:
    def __init__(self, username: str, attributes: dict):
        self.username = username
        self.attributes = (
            # e.g. {'department': 'engineering', 'clearance': 'high', ...}
            attributes
        )


class Tool:
    def __init__(self, name: str, action: str, attributes: dict):
        self.name = name
        self.action = action
        self.attributes = (
            # e.g. {'sensitivity': 'high', 'scope': 'production', ...}
            attributes
        )


class Context:
    """Execution context of the operation."""

    def __init__(self, environment: str, time_of_day: int):
        self.environment = environment  # 'dev', 'staging', 'production'
        self.time_of_day = time_of_day  # hour of the day (0–23)


class ABACPolicy:
    """
    Attribute-Based Access Control (ABAC) policy.
    Each rule represents a condition for granting access.
    """

    @staticmethod
    def evaluate(user: User, tool: Tool, context: Context) -> tuple[bool, str]:
        """
        Evaluates the access policy based on attributes.

        Returns:
            (is_allowed, reason)

        Principle: deny-by-default — access is denied
        unless explicitly allowed.
        """

        if user.attributes.get("role") == "admin":
            return True, "Administrator privileges"

        if context.environment == "production" and tool.action == "delete":
            return False, "Delete operations are not allowed in production"

        if tool.attributes.get("sensitivity") == "high":
            if user.attributes.get("clearance") != "high":
                return (
                    False,
                    "High-sensitivity tools require high clearance level",
                )

        if tool.name == "database" and tool.action in ["write", "delete"]:
            if not (9 <= context.time_of_day <= 18):
                return (
                    False,
                    "Database write/delete operations are allowed"
                    "only during business hours (9–18)",
                )

        if tool.name == "filesystem":
            if user.attributes.get("department") != "engineering":
                return (
                    False,
                    "Filesystem tools are available only to"
                    "department=engineering",
                )
            if tool.action == "write" and context.environment != "dev":
                return (
                    False,
                    "Write operations are allowed only in dev environment"
                )

        if tool.name == "http_client":
            clearance = user.attributes.get("clearance", "none")
            if clearance not in ["medium", "high"]:
                return False, "HTTP client requires at least clearance=medium"

        if tool.action == "read":
            return True, "Read access granted"

        return False, "No matching policy found — access denied by default"


# Usage examples
user1 = User(
    "Alice", {
        "role": "developer",
        "department": "engineering",
        "clearance": "high"
    }
)

user2 = User(
    "Bob", {
        "role": "analyst",
        "department": "marketing",
        "clearance": "low"
    }
)

# Tools
tool_db_delete = Tool("database", "delete", {"sensitivity": "high"})
tool_db_read = Tool("database", "read", {"sensitivity": "low"})
tool_fs_write = Tool("filesystem", "write", {"sensitivity": "medium"})

# Contexts
context_prod = Context("production", 14)  # Production, 14:00
context_dev = Context("dev", 10)  # Dev, 10:00
context_night = Context("dev", 22)  # Dev, 22:00

policy = ABACPolicy()

allowed, reason = policy.evaluate(user1, tool_db_delete, context_prod)
print(f"Alice attempts to delete in production: {allowed} - {reason}")  # False

allowed, reason = policy.evaluate(user1, tool_db_read, context_prod)
print(f"Alice reads the database: {allowed} - {reason}")  # True

allowed, reason = policy.evaluate(user2, tool_fs_write, context_dev)
print(f"Bob attempts to access filesystem: {allowed} - {reason}")  # False

allowed, reason = policy.evaluate(user1, tool_fs_write, context_dev)
print(f"Alice writes to filesystem in dev: {allowed} - {reason}")  # True

allowed, reason = policy.evaluate(user1, tool_db_delete, context_night)
print(f"Alice attempts to delete at night: {allowed} - {reason}")  # False
