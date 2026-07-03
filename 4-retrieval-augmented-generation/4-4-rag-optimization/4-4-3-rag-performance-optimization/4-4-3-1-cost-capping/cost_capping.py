import time

from langchain_core.documents import Document


def build_docs() -> list[Document]:
    """Build sample retrieved documents.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content='Cost-capping limits resources per RAG query.',
            metadata={'id': 'doc_1', 'score': 0.91},
        ),
        Document(
            page_content='Reranking improves precision but increases latency.',
            metadata={'id': 'doc_2', 'score': 0.78},
        ),
        Document(
            page_content='Early stopping can skip expensive later stages.',
            metadata={'id': 'doc_3', 'score': 0.88},
        ),
    ]
    return docs_list


def check_budget(
    start_time: float,
    budget_seconds: float,
) -> bool:
    """Check whether time budget is still available.
    Args:
        start_time (float): Pipeline start timestamp.
        budget_seconds (float): Maximum allowed processing time."""
    elapsed_seconds = time.perf_counter() - start_time
    has_budget = elapsed_seconds < budget_seconds
    return has_budget


def dedupe_docs(docs_list: list[Document]) -> list[Document]:
    """Remove duplicate documents by content.
    Args:
        docs_list (list[Document]): Documents for deduplication."""
    seen_contents = set()
    unique_docs = []

    for doc_item in docs_list:
        if doc_item.page_content in seen_contents:
            continue

        seen_contents.add(doc_item.page_content)
        unique_docs.append(doc_item)

    return unique_docs


def rerank_docs(
    docs_list: list[Document],
    top_n: int,
) -> list[Document]:
    """Rerank documents by metadata score.
    Args:
        docs_list (list[Document]): Documents for reranking.
        top_n (int): Number of top documents to return."""
    sorted_docs = sorted(
        docs_list,
        key=lambda doc_item: doc_item.metadata.get('score', 0.0),
        reverse=True,
    )
    reranked_docs = sorted_docs[:top_n]
    return reranked_docs


def retrieve_docs(
    budget_seconds: float,
    top_n: int,
) -> list[Document]:
    """Run retrieval with time budget limit.
    Args:
        budget_seconds (float): Maximum allowed processing time.
        top_n (int): Number of final documents."""
    start_time = time.perf_counter()

    if not check_budget(
        start_time=start_time,
        budget_seconds=budget_seconds,
    ):
        return []

    docs_list = build_docs()
    unique_docs = dedupe_docs(docs_list=docs_list)

    if not check_budget(
        start_time=start_time,
        budget_seconds=budget_seconds,
    ):
        return unique_docs[:top_n]

    reranked_docs = rerank_docs(
        docs_list=unique_docs,
        top_n=top_n,
    )
    return reranked_docs


def print_docs(docs_list: list[Document]) -> list[Document]:
    """Print retrieved documents.
    Args:
        docs_list (list[Document]): Documents for output."""
    for index, doc_item in enumerate(docs_list, start=1):
        print(f'Result {index}:')
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)

    return docs_list


if __name__ == '__main__':
    final_docs = retrieve_docs(
        budget_seconds=2.0,
        top_n=2,
    )
    printed_docs = print_docs(docs_list=final_docs)
