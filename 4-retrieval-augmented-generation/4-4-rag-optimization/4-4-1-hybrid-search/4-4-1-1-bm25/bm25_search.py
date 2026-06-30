import re

import numpy as np
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi


TOKEN_RE = re.compile(r'[A-Za-zА-Яа-я0-9_]+', re.UNICODE)


def build_docs() -> list[Document]:
    """Build sample documents for BM25 search.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content='BM25 is useful for exact keyword search.',
            metadata={'id': 'doc_1', 'topic': 'search'},
        ),
        Document(
            page_content='Vector search finds documents by semantic meaning.',
            metadata={'id': 'doc_2', 'topic': 'embeddings'},
        ),
        Document(
            page_content='Python pandas DataFrame is a common data object.',
            metadata={'id': 'doc_3', 'topic': 'python'},
        ),
        Document(
            page_content='Hybrid search combines BM25 and vector retrieval.',
            metadata={'id': 'doc_4', 'topic': 'rag'},
        ),
    ]
    return docs_list


def tokenize_text(text: str) -> list[str]:
    """Tokenize text for BM25.
    Args:
        text (str): Input text for tokenization."""
    tokens_list = [
        token.lower()
        for token in TOKEN_RE.findall(text)
    ]
    return tokens_list


def build_bm25(docs_list: list[Document]) -> BM25Okapi:
    """Build BM25 index from documents.
    Args:
        docs_list (list[Document]): Documents for indexing."""
    corpus_list = [
        doc_item.page_content
        for doc_item in docs_list
    ]
    tokenized_corpus = [
        tokenize_text(text=doc_text)
        for doc_text in corpus_list
    ]

    bm25_index = BM25Okapi(tokenized_corpus)
    return bm25_index


def build_doc_map(docs_list: list[Document]) -> dict[str, Document]:
    """Build document map by metadata id.
    Args:
        docs_list (list[Document]): Documents for mapping."""
    doc_map = {
        str(doc_item.metadata.get('id', index)): doc_item
        for index, doc_item in enumerate(docs_list)
    }
    return doc_map


def search_bm25(
    bm25_index: BM25Okapi,
    docs_list: list[Document],
    query: str,
    top_k: int,
) -> dict[str, float]:
    """Search documents with BM25.
    Args:
        bm25_index (BM25Okapi): Built BM25 index.
        docs_list (list[Document]): Original documents.
        query (str): Search query.
        top_k (int): Number of top results."""
    query_tokens = tokenize_text(text=query)
    scores = bm25_index.get_scores(query_tokens)
    top_indices = np.argsort(scores)[::-1][:top_k]

    results_map = {}

    for index in top_indices:
        doc_id = str(docs_list[index].metadata.get('id', index))
        results_map[doc_id] = float(scores[index])

    return results_map


def print_results(
    results_map: dict[str, float],
    doc_map: dict[str, Document],
) -> dict[str, float]:
    """Print BM25 search results.
    Args:
        results_map (dict[str, float]): BM25 scores by document id.
        doc_map (dict[str, Document]): Documents by document id."""
    for doc_id, score_value in results_map.items():
        doc_item = doc_map[doc_id]
        print(f'Document ID: {doc_id}')
        print(f'BM25 score: {score_value:.4f}')
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)

    return results_map


if __name__ == '__main__':
    docs_list = build_docs()
    doc_map = build_doc_map(docs_list=docs_list)
    bm25_index = build_bm25(docs_list=docs_list)

    results_map = search_bm25(
        bm25_index=bm25_index,
        docs_list=docs_list,
        query='Python pandas DataFrame',
        top_k=3,
    )
    printed_results = print_results(
        results_map=results_map,
        doc_map=doc_map,
    )
