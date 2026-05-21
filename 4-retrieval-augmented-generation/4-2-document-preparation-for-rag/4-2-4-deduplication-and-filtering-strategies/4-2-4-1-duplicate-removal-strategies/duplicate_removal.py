import hashlib

from langchain_core.documents import Document


def build_docs() -> list[Document]:
    """Build sample documents with duplicates.
    Args:
        None (type): No arguments."""
    docs_list = [
        Document(
            page_content='Retrieval works on chunk embeddings.',
            metadata={'source': 'rag_notes', 'page': 1},
        ),
        Document(
            page_content='Retrieval works on chunk embeddings.',
            metadata={'source': 'rag_notes_copy', 'page': 1},
        ),
        Document(
            page_content='Chunk overlap preserves context boundaries.',
            metadata={'source': 'chunking_notes', 'page': 2},
        ),
        Document(
            page_content='Chunk overlap preserves context boundaries.',
            metadata={'source': 'chunking_notes_copy', 'page': 3},
        ),
        Document(
            page_content='Metadata improves search transparency.',
            metadata={'source': 'metadata_notes', 'page': 4},
        ),
    ]
    return docs_list


def build_hash(text: str) -> str:
    """Build md5 hash for text.
    Args:
        text (str): Input text for hashing."""
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return text_hash


def dedupe_docs(docs_list: list[Document]) -> list[Document]:
    """Remove exact duplicate documents by text hash.
    Args:
        docs_list (list[Document]): Documents for deduplication."""
    unique_hashes = set()
    unique_docs = []

    for doc_item in docs_list:
        text_value = doc_item.page_content.strip()
        text_hash = build_hash(text=text_value)

        if text_hash in unique_hashes:
            continue

        unique_hashes.add(text_hash)
        unique_docs.append(doc_item)

    return unique_docs


def print_docs(docs_list: list[Document]) -> list[Document]:
    """Print documents with metadata.
    Args:
        docs_list (list[Document]): Documents for output."""
    for index, doc_item in enumerate(docs_list, start=1):
        print(f'Document {index}:')
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)

    return docs_list


if __name__ == '__main__':
    docs_list = build_docs()
    unique_docs = dedupe_docs(docs_list=docs_list)
    printed_docs = print_docs(docs_list=unique_docs)
