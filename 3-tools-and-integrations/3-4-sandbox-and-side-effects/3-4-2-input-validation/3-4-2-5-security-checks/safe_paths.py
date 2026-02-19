from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SafePathResult:
    ok: bool
    path: Path | None
    error: str | None


def safe_path(user_path: str, base_dir: Path) -> SafePathResult:
    """
    Ensure user_path stays within base_dir after normalization.
    Protects against path traversal and prefix tricks.

    Deny-by-default: if validation fails, return ok=False.
    """
    base = base_dir.resolve()

    try:
        candidate = (base / user_path).resolve()
    except Exception as exc:
        return SafePathResult(False, None, f"failed to resolve path: {exc}")

    if candidate.is_absolute() is False:
        # resolve() should always return absolute; if not, treat as suspicious
        return SafePathResult(False, None, "resolved path is not absolute")

    if not candidate.is_relative_to(base):
        return SafePathResult(False, None, "path escape detected")

    return SafePathResult(True, candidate, None)


def main() -> None:
    base_dir = Path("./sandbox").resolve()

    examples = [
        "user_files/document.txt",
        "../../etc/passwd",
        "../sandbox2/file.txt",
        "/etc/passwd",
    ]

    for p in examples:
        result = safe_path(p, base_dir=base_dir)
        print('\n', p, "=>", result)


if __name__ == "__main__":
    main()
