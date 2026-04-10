import re


def remove_footer(text: str) -> str:
    """Remove repeating footer pattern from text.
    Args:
        text (str): Input text."""
    cleaned_text = re.sub(
        r'Company\s+Confidential\s+\d{4}\.\s+All rights reserved\.',
        ' ',
        text,
    )
    return cleaned_text


def remove_content_block(text: str) -> str:
    """Remove placeholder content block from text.
    Args:
        text (str): Input text."""
    cleaned_text = re.sub(r'\.{3,}Contents\.{3,}', ' ', text)
    return cleaned_text


def clean_symbols(text: str) -> str:
    """Remove noisy symbols and normalize spaces.
    Args:
        text (str): Input text."""
    cleaned_text = text.encode('utf-8', 'ignore').decode('utf-8')
    cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
    cleaned_text = re.sub(r'\n{2,}', '\n', cleaned_text)
    return cleaned_text.strip()


def clean_text(text: str) -> str:
    """Apply noise cleaning pipeline to text.
    Args:
        text (str): Input text."""
    cleaned_text = remove_footer(text=text)
    cleaned_text = remove_content_block(text=cleaned_text)
    cleaned_text = clean_symbols(text=cleaned_text)
    return cleaned_text


if __name__ == '__main__':
    raw_text = (
        'Article 1. General section\n\n'
        'Company Confidential 2024. All rights reserved.\n'
        'Introduction: This document explains the policy.\n'
        '...Contents...\n'
        'Article 2. Next section'
    )

    cleaned_text = clean_text(text=raw_text)
    print(cleaned_text)
