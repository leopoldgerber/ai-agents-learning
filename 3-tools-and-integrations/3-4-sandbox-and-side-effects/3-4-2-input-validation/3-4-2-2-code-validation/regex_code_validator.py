import re
from dataclasses import dataclass
from typing import Optional, Set, Tuple


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    error: Optional[str]


class RegexCodeValidator:
    """Lightweight regex-based code validation (deny-by-default)."""

    MAX_CODE_LENGTH = 10_000

    DANGEROUS_PATTERNS: Tuple[Tuple[str, str], ...] = (
        (r"\bos\.system\b", "os.system usage is forbidden"),
        (r"\beval\s*\(", "eval() usage is forbidden"),
        (r"\bexec\s*\(", "exec() usage is forbidden"),
        (r"\b__import__\s*\(", "__import__ usage is forbidden"),
        (r"\bsubprocess\b", "subprocess usage is forbidden"),
        (r"\bsocket\b", "socket usage is forbidden"),
        (r"\bopen\s*\(.*[\"']w[\"']", "file write is restricted"),
    )

    ALLOWED_IMPORTS: Set[str] = {
        "math",
        "json",
        "datetime",
        "collections",
        "re",
        "statistics",
        "itertools",
        "random",
    }

    @classmethod
    def validate(cls, code: str) -> ValidationResult:
        """Return ValidationResult with deny-by-default behavior."""
        if len(code) > cls.MAX_CODE_LENGTH:
            return ValidationResult(False, "code exceeds maximum length")

        for pattern, message in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, code, flags=re.IGNORECASE):
                return ValidationResult(
                    False, f"dangerous pattern detected: {message}")

        for module in cls._extract_imports(code):
            if module not in cls.ALLOWED_IMPORTS:
                return ValidationResult(False, f"import not allowed: {module}")

        return ValidationResult(True, None)

    @staticmethod
    def _extract_imports(code: str) -> Set[str]:
        """
        Extract root import modules from simple patterns:
        - import x
        - from x import y
        This is intentionally simplistic (regex-based).
        """
        imports: Set[str] = set()

        for match in re.findall(
                r"^\s*import\s+([a-zA-Z_]\w*)", code, flags=re.MULTILINE):
            imports.add(match)

        for match in re.findall(
            r"^\s*from\s+([a-zA-Z_]\w*)\s+import\s+",
            code,
            flags=re.MULTILINE,
        ):
            imports.add(match)

        return imports


def main() -> None:
    safe_code = """
        import math
        print(math.sqrt(16))
    """

    dangerous_code = """
        import os
        os.system("rm -rf /")
    """

    safe_result = RegexCodeValidator.validate(safe_code)
    print("safe:", safe_result)

    danger_result = RegexCodeValidator.validate(dangerous_code)
    print("danger:", danger_result)


if __name__ == "__main__":
    main()
