import ast
from pathlib import Path

# Security configuration
FORBIDDEN_NAMES = {
    "os", "sys", "subprocess", "socket",
    "requests", "urllib", "eval", "exec",
    "__import__", "pickle", "shutil"
}

ALLOWED_MODULES = {
    "pandas", "numpy", "matplotlib", "seaborn",
    "scipy", "datetime", "math", "json",
    "csv", "re", "collections", "itertools"
}

SANDBOX_DIR = Path("./sandbox").resolve()


class ASTCodeValidator(ast.NodeVisitor):
    """
    Advanced code validation via AST analysis.
    Understands code structure and checks usage context.
    """

    def __init__(self):
        self.errors = []

    def visit_Import(self, node):
        """Validates regular imports: `import module`."""
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root not in ALLOWED_MODULES:
                self.errors.append(
                    f"Module '{root}' is not allowed (line {node.lineno})")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Validates `from` imports: `from module import name`."""
        if node.module is None:
            self.errors.append(
                f"Relative imports are forbidden (line {node.lineno})")
            return
        root = node.module.split(".")[0]
        if root not in ALLOWED_MODULES:
            self.errors.append(
                f"Module '{root}' is not allowed (line {node.lineno})")
        self.generic_visit(node)

    def visit_Call(self, node):
        """Validates function calls."""
        # Direct calls: eval(), exec(), __import__()
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_NAMES:
                self.errors.append(
                    f"Forbidden function: {node.func.id} (line {node.lineno})"
                )

        # Method calls: os.system(), subprocess.run()
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_NAMES:
                self.errors.append(
                    f"Forbidden method: {node.func.attr} (line {node.lineno})"
                )

        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Validates attribute access."""
        # Block dunder attributes to prevent sandbox escape
        # Example: __class__.__bases__[0].__subclasses__()
        if node.attr.startswith("__") and node.attr.endswith("__"):
            self.errors.append(
                "Access to dunder attribute "
                f"'{node.attr}' is forbidden (line {node.lineno})"
            )
        self.generic_visit(node)

    def visit_Constant(self, node):
        """
        Checks string constants for dangerous file paths.
        This is critical for preventing Path Traversal attacks.
        """
        if isinstance(node.value, str):
            try:
                # Check whether it looks like a file path
                if (
                    "/" in node.value
                    or "\\" in node.value
                    or node.value.startswith(".")
                ):
                    p = Path(node.value)

                    # Absolute paths or paths escaping the sandbox
                    # are forbidden
                    if p.is_absolute():
                        self.errors.append(
                            "Absolute path is forbidden: "
                            f"{node.value} (line {node.lineno})"
                        )
                    else:
                        # Validate relative path
                        resolved = (SANDBOX_DIR / p).resolve()
                        if not resolved.is_relative_to(SANDBOX_DIR):
                            self.errors.append(
                                "Path escapes the sandbox: "
                                f"{node.value} (line {node.lineno})"
                            )
            except Exception:
                # If it cannot be parsed as a path, ignore it
                pass

        self.generic_visit(node)


def validate_code_ast(code: str) -> tuple[bool, list]:
    """
    Validates code via AST analysis.
    Returns (is_valid, list_of_errors).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"Syntax error: {e}"]

    validator = ASTCodeValidator()
    validator.visit(tree)

    if validator.errors:
        return False, validator.errors

    return True, []


if __name__ == '__main__':
    # Usage examples
    print("=== Test 1: Safe code ===")
    safe_code = """
    import pandas as pd
    import numpy as np

    data = {'x': [1, 2, 3], 'y': [4, 5, 6]}
    df = pd.DataFrame(data)
    print(df.mean())
    """
    is_valid, errors = validate_code_ast(safe_code)
    print(f"Result: {'✅ Safe' if is_valid else '❌ Unsafe'}")
    if errors:
        for error in errors:
            print(f"  - {error}")

    print("\n=== Test 2: Attempt to import a forbidden module ===")
    dangerous_code1 = """
    import requests
    data = requests.get("https://evil.com")
    """
    is_valid, errors = validate_code_ast(dangerous_code1)
    print(f"Result: {'✅ Safe' if is_valid else '❌ Unsafe'}")
    if errors:
        for error in errors:
            print(f"  - {error}")

    print("\n=== Test 3: Attempt to use eval() ===")
    dangerous_code2 = """
    import math
    code = "print('hacked')"
    eval(code)
    """
    is_valid, errors = validate_code_ast(dangerous_code2)
    print(f"Result: {'✅ Safe' if is_valid else '❌ Unsafe'}")
    if errors:
        for error in errors:
            print(f"  - {error}")

    print("\n=== Test 4: Path Traversal attack ===")
    dangerous_code3 = """
    import pandas as pd
    df = pd.read_csv('../../etc/passwd')
    """
    is_valid, errors = validate_code_ast(dangerous_code3)
    print(f"Result: {'✅ Safe' if is_valid else '❌ Unsafe'}")
    if errors:
        for error in errors:
            print(f"  - {error}")

    print("\n=== Test 5: Attempt to bypass via dunder attributes ===")
    dangerous_code4 = """
    import math
    # Attempt to access built-ins via __class__
    obj = math
    bases = obj.__class__.__bases__
    """
    is_valid, errors = validate_code_ast(dangerous_code4)
    print(f"Result: {'✅ Safe' if is_valid else '❌ Unsafe'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
