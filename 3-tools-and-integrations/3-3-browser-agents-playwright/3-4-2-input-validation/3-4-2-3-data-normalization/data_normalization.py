import html
import re


MAX_LENGTH = 5000


def normalize_whitespace(text: str) -> str:
    """Collapse excessive whitespace."""
    return " ".join(text.split())


def remove_control_chars(text: str) -> str:
    """Remove non-printable control characters."""
    return re.sub(r"[\x00-\x1F\x7F]", "", text)


def limit_length(text: str, max_len: int = MAX_LENGTH) -> str:
    """Limit text length to protect model and logs."""
    if len(text) > max_len:
        return text[:max_len] + "... [truncated]"
    return text


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return html.escape(text)


def normalize_for_model(raw_text: str) -> str:
    """
    Full normalization pipeline before sending data to model.
    """
    text = remove_control_chars(raw_text)
    text = normalize_whitespace(text)
    text = limit_length(text)
    return text


def main() -> None:
    raw = """
        <script>alert('xss')</script>

        Some    useful   content.

        \x00\x01
    """

    cleaned = normalize_for_model(raw)
    escaped = escape_html(cleaned)

    print("normalized:", cleaned)
    print("escaped:", escaped)


if __name__ == "__main__":
    main()
