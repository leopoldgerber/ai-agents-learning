from langchain_core.documents import Document
from sentence_transformers import CrossEncoder


def build_docs() -> list[Document]:
    """Build sample candidate documents.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content=(
                'HNSW is a graph-based index for approximate '
                'nearest neighbor search.'
            ),
            metadata={'id': 'doc_1', 'source': 'index_notes'},
        ),
        Document(
            page_content=(
                'HNSW can use more RAM because it stores graph '
                'connections in addition to vectors.'
            ),
            metadata={'id': 'doc_2', 'source': 'memory_notes'},
        ),
        Document(
            page_content=(
                'BM25 is a lexical retrieval method based on exact '
                'keyword matching.'
            ),
            metadata={'id': 'doc_3', 'source': 'hybrid_notes'},
        ),
    ]
    return docs_list


def build_pairs(
    query: str,
    docs_list: list[Document],
) -> list[list[str]]:
    """Build query-document pairs for cross-encoder.
    Args:
        query (str): Search query.
        docs_list (list[Document]): Candidate documents."""
    pairs_list = [
        [query, doc_item.page_content]
        for doc_item in docs_list
    ]
    return pairs_list


def score_pairs(
    model_name: str,
    pairs_list: list[list[str]],
) -> list[float]:
    """Score query-document pairs with cross-encoder.
    Args:
        model_name (str): Cross-encoder model name.
        pairs_list (list[list[str]]): Query-document text pairs."""
    model = CrossEncoder(model_name)
    scores_list = model.predict(pairs_list)

    return [
        float(score_value)
        for score_value in scores_list
    ]


def rerank_docs(
    docs_list: list[Document],
    scores_list: list[float],
    top_n: int,
) -> list[Document]:
    """Rerank documents by cross-encoder scores.
    Args:
        docs_list (list[Document]): Candidate documents.
        scores_list (list[float]): Relevance scores.
        top_n (int): Number of top documents to return."""
    doc_score_pairs = list(zip(docs_list, scores_list))
    doc_score_pairs.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    reranked_docs = []

    for doc_item, score_value in doc_score_pairs[:top_n]:
        doc_item.metadata['rerank_score'] = float(score_value)
        reranked_docs.append(doc_item)

    return reranked_docs


def print_docs(docs_list: list[Document]) -> list[Document]:
    """Print reranked documents.
    Args:
        docs_list (list[Document]): Documents for output."""
    for index, doc_item in enumerate(docs_list, start=1):
        print(f'Rank {index}:')
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)

    return docs_list


if __name__ == '__main__':
    query = 'Why can HNSW become expensive for large datasets?'
    docs_list = build_docs()
    pairs_list = build_pairs(
        query=query,
        docs_list=docs_list,
    )
    scores_list = score_pairs(
        model_name='cross-encoder/ms-marco-MiniLM-L-6-v2',
        pairs_list=pairs_list,
    )
    reranked_docs = rerank_docs(
        docs_list=docs_list,
        scores_list=scores_list,
        top_n=2,
    )
    printed_docs = print_docs(docs_list=reranked_docs)
