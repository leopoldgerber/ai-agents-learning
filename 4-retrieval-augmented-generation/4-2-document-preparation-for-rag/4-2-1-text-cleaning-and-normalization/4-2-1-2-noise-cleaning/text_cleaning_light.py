import re


raw_text = """Article 1. General provision

Company Confidential 2024. All rights reserved.
Introduction: This document...
...Contents...
1.1. Definitions.

Article 2. Next section"""


def clean_text(text: str) -> str:
    # Remove mentions of 'Company Confidential ...'
    text = re.sub(
        r'Company\s+Confidential\s+\d{4}\.\s+All rights reserved\.',
        ' ',
        text
    )
    # Remove 'Contents...' as an example of an unnecessary section
    text = re.sub(r'\.{3,}Contents\.{3,}', ' ', text)
    # Remove extra line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n', ' ', text)
    # Remove multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


cleaned = clean_text(raw_text)
print(cleaned)
# Output: Article 1. General provision Introduction: This document...
# 1.1. Definitions. Article 2. Next section
