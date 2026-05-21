from langchain_core.documents import Document


def build_docs(
    pages_list: list[str],
    source_name: str,
    topic_name: str,
) -> list[Document]:
    """Build documents with metadata.
    Args:
        pages_list (list[str]): List of page texts.
        source_name (str): Source name for all pages.
        topic_name (str): Topic name for all pages."""
    docs_list = []

    for page_number, page_text in enumerate(pages_list, start=1):
        doc_item = Document(
            page_content=page_text,
            metadata={
                'source': source_name,
                'page': page_number,
                'topic': topic_name,
                'language': 'de',
            },
        )
        docs_list.append(doc_item)

    return docs_list


def filter_docs(
    docs_list: list[Document],
    topic_name: str,
) -> list[Document]:
    """Filter documents by topic metadata.
    Args:
        docs_list (list[Document]): Documents with metadata.
        topic_name (str): Topic value for filtering."""
    filtered_docs = [
        doc_item
        for doc_item in docs_list
        if doc_item.metadata.get('topic') == topic_name
    ]
    return filtered_docs


def print_docs(docs_list: list[Document]) -> list[Document]:
    """Print documents and their metadata.
    Args:
        docs_list (list[Document]): Documents for output."""
    for index, doc_item in enumerate(docs_list, start=1):
        print(f'Document {index}:')
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)

    return docs_list


if __name__ == '__main__':
    pages_list = [
        'Embedding models convert text into vectors.',
        'Metadata helps filter and explain search results.',
        'Chunks need both text and contextual information.',
    ]

    docs_list = build_docs(
        pages_list=pages_list,
        source_name='rag_notes.pdf',
        topic_name='rag',
    )
    filtered_docs = filter_docs(
        docs_list=docs_list,
        topic_name='rag',
    )
    printed_docs = print_docs(docs_list=filtered_docs)
