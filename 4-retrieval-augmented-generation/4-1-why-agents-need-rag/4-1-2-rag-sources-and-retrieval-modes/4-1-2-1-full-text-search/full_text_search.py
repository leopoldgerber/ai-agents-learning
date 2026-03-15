from typing import List


def normalize_text(text: str) -> str:
    """Normalize text for search.
    Args:
        text (str): Input text."""
    return text.lower().strip()


def full_text_search(documents: List[str], query: str) -> List[str]:
    """Return documents containing query words.
    Args:
        documents (List[str]): List of text documents.
        query (str): User search query."""
    normalized_query = normalize_text(query)

    results: List[str] = []

    for document in documents:
        normalized_doc = normalize_text(document)

        if normalized_query in normalized_doc:
            results.append(document)

    return results


if __name__ == "__main__":
    documents = [
        "AI research is evolving quickly",
        "Machine learning improves predictions",
        "Deep learning techniques in AI systems",
        "New advances in robotics"
    ]

    query = "AI"

    matches = full_text_search(documents, query)

    for match in matches:
        print(match)
