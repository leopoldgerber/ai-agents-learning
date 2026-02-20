import os
import ast
import json
import signal
import hashlib
import logging
import platform
import subprocess
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import resource only on Unix systems.
RESOURCE_AVAILABLE = False
if platform.system() != "Windows":
    try:
        import resource  # type: ignore

        RESOURCE_AVAILABLE = True
    except ImportError:
        pass

# ============= LOGGING SETUP =============
logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="%(message)s"
)


class ExecutionStatus(Enum):
    """Execution status values."""

    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"
    RESOURCE_LIMIT = "resource_limit"


class ImmutableAuditLog:
    """Append-only audit log using a cryptographic hash chain."""

    def __init__(self) -> None:
        self.chain: List[Dict[str, object]] = []

    def add_entry(
        self,
        user: str,
        action: str,
        status: str,
        details: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        """Add an entry to the hash chain and write it to the log."""
        prev_hash = self.chain[-1]["hash"] if self.chain else "0" * 64
        entry: Dict[str, object] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user": user,
            "action": action,
            "status": status,
            "details": details or {},
            "prev_hash": prev_hash,
        }

        # Hash the entry data (excluding the `hash` field itself).
        entry_str = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(entry_str.encode()).hexdigest()

        self.chain.append(entry)
        logging.info(json.dumps(entry))
        return entry


class AccessControl:
    """Role-based access control (RBAC)."""

    def __init__(self) -> None:
        self.permissions = {
            "admin": ["read", "write", "execute", "delete"],
            "developer": ["read", "write", "execute"],
            "analyst": ["read", "execute"],
            "viewer": ["read"],
        }

    def can_access(self, role: str, action: str) -> bool:
        """Return True if `role` is allowed to perform `action`."""
        return action in self.permissions.get(role, [])


SANDBOX_DIR = Path("./sandbox").resolve()


class ASTCodeValidator(ast.NodeVisitor):
    """Advanced AST-based code validation with contextual checks."""

    # Extended list of forbidden names to reduce bypass attempts.
    FORBIDDEN_NAMES = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "eval",
        "exec",
        "__import__",
        "pickle",
        "shutil",
        "getattr",
        "setattr",
        "hasattr",
        "globals",
        "locals",
        "dir",
    }

    ALLOWED_MODULES = {
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "scipy",
        "datetime",
        "time",
        "math",
        "json",
        "csv",
        "re",
        "collections",
        "itertools",
    }

    def __init__(self) -> None:
        self.errors: List[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Validate standard imports: `import module`."""
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root not in self.ALLOWED_MODULES:
                self.errors.append(
                    f"Module '{root}' is not allowed (line {node.lineno})"
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Validate `from module import name` imports."""
        if node.module is None:
            self.errors.append(
                f"Relative imports are forbidden (line {node.lineno})")
            return

        root = node.module.split(".")[0]
        if root not in self.ALLOWED_MODULES:
            self.errors.append(
                f"Module '{root}' is not allowed (line {node.lineno})")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Validate function and method calls."""
        # Direct calls (e.g., eval(...)).
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_NAMES:
                self.errors.append(
                    f"Forbidden function: {node.func.id} (line {node.lineno})"
                )
        # Attribute calls (e.g., os.system(...)).
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in self.FORBIDDEN_NAMES:
                self.errors.append(
                    f"Forbidden method: {node.func.attr} (line {node.lineno})"
                )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Validate attribute access."""
        # Block dunder attributes (__class__, __subclasses__, etc.).
        if node.attr.startswith("__"):
            self.errors.append(
                f"Access to dunder attribute '{node.attr}' is forbidden "
                f"(line {node.lineno})"
            )
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        """Detect dangerous file paths in string constants (path traversal)."""
        if isinstance(node.value, str):
            try:
                looks_like_path = (
                    "/" in node.value
                    or "\\" in node.value
                    or node.value.startswith(".")
                )
                if looks_like_path:
                    p = Path(node.value)

                    # Absolute paths
                    # or paths escaping the sandbox are forbidden.
                    if p.is_absolute():
                        self.errors.append(
                            f"Absolute path is forbidden: {node.value} "
                            f"(line {node.lineno})"
                        )
                    else:
                        resolved = (SANDBOX_DIR / p).resolve()
                        if not resolved.is_relative_to(SANDBOX_DIR):
                            self.errors.append(
                                f"Path escapes sandbox: {node.value} "
                                f"(line {node.lineno})"
                            )
            except Exception:
                # If parsing as a path fails, ignore it.
                pass

        self.generic_visit(node)

    def validate(self, code: str) -> Tuple[bool, List[str]]:
        """Validate a code string and return (ok, list_of_errors)."""
        self.errors = []
        try:
            tree = ast.parse(code)
            self.visit(tree)
        except SyntaxError as exc:
            return False, [f"Syntax error: {exc}"]
        return len(self.errors) == 0, self.errors


def set_resource_limits() -> None:
    """Apply OS-level resource limits (Unix only)."""
    if not RESOURCE_AVAILABLE:
        return

    try:
        # Memory limit: 100 MB.
        resource.setrlimit(
            resource.RLIMIT_AS, (100 * 1024 * 1024, 100 * 1024 * 1024)
        )

        # CPU time limit: 5 seconds.
        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))

        # File size limit: 10 MB.
        resource.setrlimit(
            resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024)
        )

        # Process count limit: 10.
        resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
    except (ValueError, OSError) as exc:
        print(f"Warning: failed to set resource limits: {exc}")


class SecureExecutionHarness:
    """Secure harness for code execution with layered protections.

    Works on Windows, Linux, and macOS.
    """

    def __init__(self) -> None:
        self.access_control = AccessControl()
        self.audit_log = ImmutableAuditLog()
        self.validator = ASTCodeValidator()

    def execute(
        self,
        code: str,
        user: str,
        user_role: str,
        timeout: int = 5,
    ) -> Dict[str, object]:
        """Validate and execute code in a restricted environment."""
        # 1) RBAC check.
        if not self.access_control.can_access(user_role, "execute"):
            self.audit_log.add_entry(
                user=user,
                action="execute_code",
                status=ExecutionStatus.BLOCKED.value,
                details={
                    "reason": "insufficient permissions",
                    "role": user_role
                },
            )
            return {
                "status": ExecutionStatus.BLOCKED.value,
                "error": "You do not have permission to execute code.",
                "output": None,
            }

        # 2) AST validation.
        is_valid, validation_errors = self.validator.validate(code)
        if not is_valid:
            self.audit_log.add_entry(
                user=user,
                action="execute_code",
                status=ExecutionStatus.BLOCKED.value,
                details={
                    "reason": "validation failed",
                    "error": validation_errors,
                    "code_length": len(code),
                },
            )
            return {
                "status": ExecutionStatus.BLOCKED.value,
                "error": f"Validation failed: {validation_errors}",
                "output": None,
            }

        # 3) Execution.
        SANDBOX_DIR.mkdir(exist_ok=True)
        self.audit_log.add_entry(
            user=user,
            action="execute_code",
            status="attempt",
            details={"code_len": len(code)},
        )

        # Environment isolation (minimal set of variables).
        is_win = platform.system() == "Windows"
        if is_win:
            sandbox_dir = os.path.join(
                os.environ.get("TEMP", "C:\\Temp"),
                "sandbox"
            )
        else:
            sandbox_dir = "/tmp/sandbox"

        os.makedirs(sandbox_dir, exist_ok=True)
        clean_env = {
            "PATH": os.environ.get("PATH", ""),
            "SystemRoot": os.environ.get("SystemRoot", ""),
            "WINDIR": os.environ.get(
                "WINDIR", os.environ.get("SystemRoot", "")),
            "TEMP": os.environ.get("TEMP", ""),
            "TMP": os.environ.get("TMP", ""),
            "HOME": sandbox_dir,
        }

        try:
            start_time = datetime.now()

            run_args: Dict[str, object] = {
                "args": ["python", "-c", code],
                "capture_output": True,
                "text": True,
                "timeout": timeout,
                "cwd": str(SANDBOX_DIR),
                "env": clean_env,
            }
            if not is_win:
                run_args["preexec_fn"] = set_resource_limits

            result = subprocess.run(**run_args)  # type: ignore[arg-type]
            execution_time = (datetime.now() - start_time).total_seconds()

            # Process results.
            status = ExecutionStatus.SUCCESS.value
            if result.returncode != 0:
                status = ExecutionStatus.FAILURE.value

                # Unix-specific signals (resource limits).
                if not is_win and result.returncode < 0:
                    sig = -result.returncode
                    if hasattr(signal, "SIGXCPU") and sig == signal.SIGXCPU:
                        status = ExecutionStatus.RESOURCE_LIMIT.value

            # 4) Final audit entry.
            self.audit_log.add_entry(
                user=user,
                action="execute_code",
                status=status,
                details={
                    "code_hash": hashlib.sha256(
                        code.encode()).hexdigest()[:16],
                    "execution_time_sec": round(execution_time, 3),
                    "output_length": len(result.stdout),
                    "return_code": result.returncode,
                    "platform": platform.system(),
                },
            )

            return {
                "status": status,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "execution_time": round(execution_time, 3),
            }

        except subprocess.TimeoutExpired:
            # Execution time exceeded.
            self.audit_log.add_entry(
                user=user,
                action="execute_code",
                status=ExecutionStatus.TIMEOUT.value,
                details={"timeout_sec": timeout},
            )
            return {
                "status": ExecutionStatus.TIMEOUT.value,
                "error": f"Maximum execution time exceeded ({timeout}s).",
                "output": None,
            }

        except subprocess.CalledProcessError as exc:
            # Execution error.
            self.audit_log.add_entry(
                user=user,
                action="execute_code",
                status=ExecutionStatus.FAILURE.value,
                details={
                    "error": str(exc),
                    "stderr": exc.stderr[:500] if exc.stderr else None,
                },
            )
            return {
                "status": ExecutionStatus.FAILURE.value,
                "error": "Code execution failed.",
                "output": exc.stderr,
            }

        except Exception as exc:
            # Unexpected error.
            self.audit_log.add_entry(
                user=user,
                action="execute_code",
                status=ExecutionStatus.FAILURE.value,
                details={"unexpected_error": type(exc).__name__},
            )
            return {
                "status": ExecutionStatus.FAILURE.value,
                "error": "Internal system error.",
                "output": None,
            }

    def get_audit_log(self) -> List[Dict[str, object]]:
        """Return the full audit log."""
        return self.audit_log.chain


if __name__ == "__main__":
    harness = SecureExecutionHarness()

    print(f"Platform: {platform.system()}\n")

    # Example 1: Successful execution of allowed code.
    print("=== Example 1: Allowed code ===")
    safe_code = """
import math
result = math.sqrt(16) + math.pi
print(f"Result: {result:.2f}")
"""
    result1 = harness.execute(safe_code, user="alice", user_role="developer")
    print(f"Status: {result1['status']}")
    print(f"Output: {result1['output']}")
    print(f"Execution time: {result1.get('execution_time')}s")

    # Example 2: Blocking dangerous code.
    print("\n=== Example 2: Dangerous code (blocked) ===")
    dangerous_code = "import os; os.system('rm -rf /')"
    result2 = harness.execute(
        dangerous_code,
        user="bob",
        user_role="developer"
    )
    print(f"Status: {result2['status']}")
    print(f"Error: {result2['error']}")

    # Example 3: Access denied.
    print("\n=== Example 3: Insufficient permissions ===")
    result3 = harness.execute(safe_code, user="charlie", user_role="viewer")
    print(f"Status: {result3['status']}")
    print(f"Error: {result3['error']}")

    # Example 4: Timeout.
    print("\n=== Example 4: Timeout exceeded ===")
    slow_code = """
import time
time.sleep(10)
print("Done")
"""
    result4 = harness.execute(
        slow_code,
        user="alice",
        user_role="developer",
        timeout=2
    )
    print(f"Status: {result4['status']}")
    print(f"Error: {result4['error']}")

    # Example 5: Attempt to use a forbidden import.
    print("\n=== Example 5: Forbidden import ===")
    forbidden_import = """
import requests
print("Making HTTP request")
"""
    result5 = harness.execute(
        forbidden_import,
        user="alice",
        user_role="developer"
    )
    print(f"Status: {result5['status']}")
    print(f"Error: {result5['error']}")

    # Print the audit log.
    print("\n=== Audit log (first 3 entries) ===")
    for entry in harness.get_audit_log()[:3]:
        print(json.dumps(entry, indent=2))
