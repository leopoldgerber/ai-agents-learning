from pathlib import Path

import torch
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder


def build_docs() -> list[Document]:
    """Build sample documents for optimized retrieval.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content='Python is used for machine learning projects.',
            metadata={'source': 'doc_1', 'category': 'ml'},
        ),
        Document(
            page_content='PyTorch is a framework for deep learning.',
            metadata={'source': 'doc_2', 'category': 'ml'},
        ),
        Document(
            page_content='JavaScript is often used for frontend apps.',
            metadata={'source': 'doc_3', 'category': 'web'},
        ),
        Document(
            page_content='Cross-encoder reranking improves precision.',
            metadata={'source': 'doc_4', 'category': 'rag'},
        ),
    ]
    return docs_list


def select_device() -> str:
    """Select device for reranker model.
    Args:
        None: No arguments."""
    if torch.cuda.is_available():
        return 'cuda'

    return 'cpu'


def build_embeddings(
    model_name: str,
) -> HuggingFaceEmbeddings:
    """Build embedding model.
    Args:
        model_name (str): Embedding model name."""
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings


def load_store(
    docs_list: list[Document],
    embeddings: HuggingFaceEmbeddings,
    index_path: Path,
) -> FAISS:
    """Load cached FAISS store or build a new one.
    Args:
        docs_list (list[Document]): Documents for index creation.
        embeddings (HuggingFaceEmbeddings): Embedding model.
        index_path (Path): Local FAISS index path."""
    if index_path.exists():
        vector_store = FAISS.load_local(
            folder_path=str(index_path),
            embeddings=embeddings,
            allow_dangerous_deserialization=True,
        )
        return vector_store

    vector_store = FAISS.from_documents(
        documents=docs_list,
        embedding=embeddings,
    )
    vector_store.save_local(folder_path=str(index_path))

    return vector_store


def search_store(
    vector_store: FAISS,
    query: str,
    candidate_count: int,
) -> list[Document]:
    """Search candidate documents in vector store.
    Args:
        vector_store (FAISS): Vector store for retrieval.
        query (str): User search query.
        candidate_count (int): Number of candidates."""
    docs_list = vector_store.similarity_search(
        query=query,
        k=candidate_count,
    )
    return docs_list


def load_reranker(
    model_name: str,
    device_name: str,
) -> CrossEncoder:
    """Load cross-encoder reranker.
    Args:
        model_name (str): Cross-encoder model name.
        device_name (str): Device for model execution."""
    reranker_model = CrossEncoder(
        model_name,
        device=device_name,
    )
    return reranker_model


def build_pairs(
    query: str,
    docs_list: list[Document],
) -> list[list[str]]:
    """Build query-document pairs.
    Args:
        query (str): User search query.
        docs_list (list[Document]): Candidate documents."""
    pairs_list = [
        [query, doc_item.page_content]
        for doc_item in docs_list
    ]
    return pairs_list


def score_batches(
    reranker_model: CrossEncoder,
    pairs_list: list[list[str]],
    batch_size: int,
) -> list[float]:
    """Score query-document pairs in batches.
    Args:
        reranker_model (CrossEncoder): Cross-encoder reranker.
        pairs_list (list[list[str]]): Query-document pairs.
        batch_size (int): Number of pairs per batch."""
    scores_list = []

    for start_index in range(0, len(pairs_list), batch_size):
        batch_pairs = pairs_list[start_index:start_index + batch_size]
        batch_scores = reranker_model.predict(batch_pairs)
        scores_list.extend(
            float(score_value)
            for score_value in batch_scores
        )

    return scores_list


def rerank_docs(
    docs_list: list[Document],
    scores_list: list[float],
    top_n: int,
) -> list[Document]:
    """Rerank documents by cross-encoder scores.
    Args:
        docs_list (list[Document]): Candidate documents.
        scores_list (list[float]): Reranker scores.
        top_n (int): Number of final documents."""
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


def print_docs(
    docs_list: list[Document],
) -> list[Document]:
    """Print final reranked documents.
    Args:
        docs_list (list[Document]): Final documents."""
    for index, doc_item in enumerate(docs_list, start=1):
        score_value = doc_item.metadata.get('rerank_score', 0.0)

        print(f'Rank {index}: score={score_value:.4f}')
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)

    return docs_list


if __name__ == '__main__':
    query = 'How can reranking improve RAG retrieval?'
    index_path = Path('./faiss_index')

    docs_list = build_docs()
    device_name = select_device()
    embeddings = build_embeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2',
    )
    vector_store = load_store(
        docs_list=docs_list,
        embeddings=embeddings,
        index_path=index_path,
    )

    candidate_docs = search_store(
        vector_store=vector_store,
        query=query,
        candidate_count=4,
    )
    reranker_model = load_reranker(
        model_name='cross-encoder/ms-marco-MiniLM-L-6-v2',
        device_name=device_name,
    )
    pairs_list = build_pairs(
        query=query,
        docs_list=candidate_docs,
    )
    scores_list = score_batches(
        reranker_model=reranker_model,
        pairs_list=pairs_list,
        batch_size=2,
    )
    reranked_docs = rerank_docs(
        docs_list=candidate_docs,
        scores_list=scores_list,
        top_n=2,
    )
    printed_docs = print_docs(docs_list=reranked_docs)
