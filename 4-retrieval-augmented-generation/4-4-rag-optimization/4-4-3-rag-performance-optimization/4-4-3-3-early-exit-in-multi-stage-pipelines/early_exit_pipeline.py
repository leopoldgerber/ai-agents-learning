from langchain_core.documents import Document


def build_vector_docs() -> list[Document]:
    """Build sample vector search results.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content='Vector search quickly finds semantic candidates.',
            metadata={'id': 'doc_1', 'score': 0.88},
        ),
        Document(
            page_content='Reranking improves precision for hard questions.',
            metadata={'id': 'doc_2', 'score': 0.74},
        ),
        Document(
            page_content='Cost-capping limits expensive RAG processing.',
            metadata={'id': 'doc_3', 'score': 0.69},
        ),
    ]
    return docs_list


def build_bm25_docs() -> list[Document]:
    """Build sample BM25 search results.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content='Early exit stops a pipeline after good results.',
            metadata={'id': 'doc_4', 'score': 0.86},
        ),
        Document(
            page_content='Vector search quickly finds semantic candidates.',
            metadata={'id': 'doc_1', 'score': 0.88},
        ),
        Document(
            page_content='Hybrid search combines BM25 and vector results.',
            metadata={'id': 'doc_5', 'score': 0.80},
        ),
    ]
    return docs_list


def search_vector(
    query: str,
    candidate_count: int,
) -> list[Document]:
    """Run sample vector search.
    Args:
        query (str): User query.
        candidate_count (int): Number of candidates to return."""
    docs_list = build_vector_docs()
    found_docs = docs_list[:candidate_count]

    return found_docs


def search_bm25(
    query: str,
    candidate_count: int,
) -> list[Document]:
    """Run sample BM25 search.
    Args:
        query (str): User query.
        candidate_count (int): Number of candidates to return."""
    docs_list = build_bm25_docs()
    found_docs = docs_list[:candidate_count]

    return found_docs


def merge_docs(
    first_docs: list[Document],
    second_docs: list[Document],
) -> list[Document]:
    """Merge and deduplicate documents by id.
    Args:
        first_docs (list[Document]): First document list.
        second_docs (list[Document]): Second document list."""
    docs_map = {}

    for doc_item in first_docs + second_docs:
        doc_id = str(doc_item.metadata.get('id'))
        current_doc = docs_map.get(doc_id)

        if current_doc is None:
            docs_map[doc_id] = doc_item
            continue

        current_score = current_doc.metadata.get('score', 0.0)
        item_score = doc_item.metadata.get('score', 0.0)

        if item_score > current_score:
            docs_map[doc_id] = doc_item

    merged_docs = sorted(
        docs_map.values(),
        key=lambda doc_item: doc_item.metadata.get('score', 0.0),
        reverse=True,
    )
    return merged_docs


def get_score(docs_list: list[Document]) -> float:
    """Get highest score from document list.
    Args:
        docs_list (list[Document]): Documents for score check."""
    if not docs_list:
        return 0.0

    score_value = max(
        doc_item.metadata.get('score', 0.0)
        for doc_item in docs_list
    )
    return float(score_value)


def rerank_docs(
    docs_list: list[Document],
    top_n: int,
) -> list[Document]:
    """Rerank documents with simulated rerank scores.
    Args:
        docs_list (list[Document]): Documents for reranking.
        top_n (int): Number of top documents to return."""
    reranked_docs = []

    for doc_item in docs_list:
        base_score = doc_item.metadata.get('score', 0.0)
        doc_item.metadata['rerank_score'] = round(base_score + 0.05, 3)
        reranked_docs.append(doc_item)

    sorted_docs = sorted(
        reranked_docs,
        key=lambda doc_item: doc_item.metadata.get('rerank_score', 0.0),
        reverse=True,
    )
    return sorted_docs[:top_n]


def retrieve_docs(
    query: str,
    confidence_threshold: float,
    final_count: int,
) -> list[Document]:
    """Run multi-stage retrieval with early exit.
    Args:
        query (str): User query.
        confidence_threshold (float): Score threshold for early exit.
        final_count (int): Number of final documents."""
    vector_docs = search_vector(
        query=query,
        candidate_count=20,
    )
    vector_score = get_score(docs_list=vector_docs)

    if vector_score >= confidence_threshold:
        return vector_docs[:final_count]

    bm25_docs = search_bm25(
        query=query,
        candidate_count=20,
    )
    merged_docs = merge_docs(
        first_docs=vector_docs,
        second_docs=bm25_docs,
    )
    merged_score = get_score(docs_list=merged_docs[:10])

    if merged_score >= confidence_threshold * 0.9:
        return merged_docs[:final_count]

    reranked_docs = rerank_docs(
        docs_list=merged_docs,
        top_n=final_count,
    )
    return reranked_docs


def print_docs(docs_list: list[Document]) -> list[Document]:
    """Print final retrieved documents.
    Args:
        docs_list (list[Document]): Final documents for output."""
    for index, doc_item in enumerate(docs_list, start=1):
        print(f'Result {index}:')
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)

    return docs_list


if __name__ == '__main__':
    final_docs = retrieve_docs(
        query='How can early exit reduce RAG latency?',
        confidence_threshold=0.95,
        final_count=3,
    )
    printed_docs = print_docs(docs_list=final_docs)
