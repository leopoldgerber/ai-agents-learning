import re


def normalize_case(text: str, to_lower: bool) -> str:
    """Normalize text case.
    Args:
        text (str): Input text.
        to_lower (bool): Whether to convert text to lowercase."""
    if to_lower:
        return text.lower()
    return text


def normalize_space(text: str) -> str:
    """Normalize spaces and line breaks.
    Args:
        text (str): Input text."""
    cleaned_text = re.sub(r'[ \t]+', ' ', text)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    cleaned_text = re.sub(r' ?\n ?', '\n', cleaned_text)
    return cleaned_text.strip()


def normalize_date(text: str) -> str:
    """Normalize simple date formats to ISO style.
    Args:
        text (str): Input text."""
    normalized_text = re.sub(
        r'\b(\d{2})\.(\d{2})\.(\d{4})\b',
        r'\3-\2-\1',
        text,
    )
    normalized_text = re.sub(
        r'\b(\d{2})/(\d{2})/(\d{4})\b',
        r'\3-\2-\1',
        normalized_text,
    )
    return normalized_text


def normalize_text(text: str, to_lower: bool) -> str:
    """Apply normalization pipeline to text.
    Args:
        text (str): Input text.
        to_lower (bool): Whether to convert text to lowercase."""
    normalized_text = normalize_space(text=text)
    normalized_text = normalize_date(text=normalized_text)
    normalized_text = normalize_case(
        text=normalized_text,
        to_lower=to_lower,
    )
    return normalized_text


if __name__ == '__main__':
    raw_text = (
        'Bericht   vom 12.03.2024\n\n'
        'Projektstatus:\t AKTIV\n\n\n'
        'Nächstes Review am 15/04/2024  '
    )

    normalized_text = normalize_text(
        text=raw_text,
        to_lower=False,
    )
    print(normalized_text)
