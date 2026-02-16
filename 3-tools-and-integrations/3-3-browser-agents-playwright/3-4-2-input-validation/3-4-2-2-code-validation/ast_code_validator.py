import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: List[str]


SANDBOX_DIR = Path("./sandbox").resolve()

FORBIDDEN_NAMES: Set[str] = {
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
}

ALLOWED_MODULES: Set[str] = {
    "math",
    "json",
    "datetime",
    "collections",
    "re",
    "statistics",
    "itertools",
    "random",
    "csv",
}


class ASTCodeValidator(ast.NodeVisitor):
    """AST-based code validator with deny-by-default behavior."""

    def __init__(self) -> None:
        self.errors: List[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root not in ALLOWED_MODULES:
                self.errors.append(
                    f"Import not allowed: '{root}' (line {node.lineno})"
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is None:
            self.errors.append(
                f"Relative import is forbidden (line {node.lineno})"
            )
            return

        root = node.module.split(".")[0]
        if root not in ALLOWED_MODULES:
            self.errors.append(
                f"Import not allowed: '{root}' (line {node.lineno})"
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Direct calls: eval(...), exec(...), __import__(...)
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_NAMES:
                self.errors.append(
                    "Forbidden function call: "
                    f"{node.func.id} (line {node.lineno})"
                )

        # Attribute calls: os.system(...), subprocess.run(...)
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_NAMES:
                self.errors.append(
                    "Forbidden method call: "
                    f"{node.func.attr} (line {node.lineno})"
                )

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # Block dunder attribute access to reduce sandbox escapes:
        # e.g. __class__.__bases__[0].__subclasses__()
        if node.attr.startswith("__") and node.attr.endswith("__"):
            self.errors.append(
                "Dunder attribute access forbidden: "
                f"{node.attr} (line {node.lineno})"
            )
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        # Detect risky paths in string constants (path traversal).
        if isinstance(node.value, str):
            value = node.value
            if "/" in value or "\\" in value or value.startswith("."):
                self._validate_path_literal(value, node.lineno)
        self.generic_visit(node)

    def _validate_path_literal(self, value: str, lineno: int) -> None:
        try:
            p = Path(value)
            if p.is_absolute():
                self.errors.append(
                    f"Absolute path forbidden: {value} (line {lineno})"
                )
                return

            resolved = (SANDBOX_DIR / p).resolve()
            if not resolved.is_relative_to(SANDBOX_DIR):
                self.errors.append(
                    f"Path escapes sandbox: {value} (line {lineno})"
                )
        except Exception:
            # If parsing fails, do not block by default here.
            # Real systems usually treat this as suspicious.
            return


def validate_code_ast(code: str) -> ValidationResult:
    """Validate code by parsing and visiting AST."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return ValidationResult(False, [f"Syntax error: {exc}"])

    validator = ASTCodeValidator()
    validator.visit(tree)

    if validator.errors:
        return ValidationResult(False, validator.errors)

    return ValidationResult(True, [])


def main() -> None:
    safe_code = """
        import math
        print(math.sqrt(16))
    """

    dangerous_code = """
        import os
        os.system("rm -rf /")
    """

    traversal_code = """
        import csv
        path = "../../etc/passwd"
        print(path)
    """

    print("safe:", validate_code_ast(safe_code))
    print("dangerous:", validate_code_ast(dangerous_code))
    print("traversal:", validate_code_ast(traversal_code))


if __name__ == "__main__":
    main()
