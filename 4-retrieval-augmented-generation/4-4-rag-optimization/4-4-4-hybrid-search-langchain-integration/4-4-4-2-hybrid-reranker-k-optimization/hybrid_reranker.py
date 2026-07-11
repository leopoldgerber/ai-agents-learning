import hashlib

from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder


class SimpleReranker:
    """Rerank candidate documents with a cross-encoder."""

    model: CrossEncoder

    def __init__(self, model_name: str) -> None:
        """Initialize cross-encoder model.
        Args:
            model_name (str): Cross-encoder model name."""
        self.model = CrossEncoder(model_name)

    def rerank_docs(
        self,
        query: str,
        docs_list: list[Document],
        top_n: int,
    ) -> list[Document]:
        """Rerank candidate documents.
        Args:
            query (str): User search query.
            docs_list (list[Document]): Candidate documents.
            top_n (int): Number of final documents."""
        if not docs_list:
            return []

        pairs_list = [
            [query, doc_item.page_content]
            for doc_item in docs_list
        ]
        scores_list = self.model.predict(pairs_list)
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


class HybridRerankerRetriever(BaseRetriever):
    """Combine two retrievers and rerank unique candidates."""

    first_retriever: BaseRetriever
    second_retriever: BaseRetriever
    reranker: SimpleReranker
    final_count: int = 3

    def dedupe_docs(
        self,
        docs_list: list[Document],
    ) -> list[Document]:
        """Remove duplicate documents by content hash.
        Args:
            docs_list (list[Document]): Documents for deduplication."""
        seen_hashes = set()
        unique_docs = []

        for doc_item in docs_list:
            content_hash = hashlib.md5(
                doc_item.page_content.encode('utf-8')
            ).hexdigest()

            if content_hash in seen_hashes:
                continue

            seen_hashes.add(content_hash)
            unique_docs.append(doc_item)

        return unique_docs

    def _get_relevant_documents(
        self,
        query: str,
    ) -> list[Document]:
        """Retrieve and rerank hybrid search results.
        Args:
            query (str): User search query."""
        first_docs = self.first_retriever.invoke(query)
        second_docs = self.second_retriever.invoke(query)

        merged_docs = first_docs + second_docs
        unique_docs = self.dedupe_docs(docs_list=merged_docs)

        reranked_docs = self.reranker.rerank_docs(
            query=query,
            docs_list=unique_docs,
            top_n=self.final_count,
        )
        return reranked_docs


def build_docs() -> list[Document]:
    """Build sample documents for hybrid retrieval.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content=(
                'Python is a programming language for machine learning.'
            ),
            metadata={'source': 'doc_1', 'category': 'programming'},
        ),
        Document(
            page_content=(
                'Machine learning uses Python and mathematics.'
            ),
            metadata={'source': 'doc_2', 'category': 'ml'},
        ),
        Document(
            page_content='JavaScript runs in web browsers.',
            metadata={'source': 'doc_3', 'category': 'web'},
        ),
        Document(
            page_content=(
                'Deep learning is a part of machine learning.'
            ),
            metadata={'source': 'doc_4', 'category': 'ml'},
        ),
        Document(
            page_content='PyTorch is a deep learning framework.',
            metadata={'source': 'doc_5', 'category': 'ml'},
        ),
    ]
    return docs_list


def build_retriever(
    docs_list: list[Document],
    candidate_count: int,
    final_count: int,
) -> HybridRerankerRetriever:
    """Build hybrid retriever with reranking.
    Args:
        docs_list (list[Document]): Documents for retrieval.
        candidate_count (int): Candidate count per retriever.
        final_count (int): Final document count."""
    embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    vector_store = FAISS.from_documents(
        documents=docs_list,
        embedding=embeddings,
    )
    vector_retriever = vector_store.as_retriever(
        search_kwargs={'k': candidate_count}
    )
    bm25_retriever = BM25Retriever.from_documents(
        documents=docs_list,
        k=candidate_count,
    )
    reranker = SimpleReranker(
        model_name='cross-encoder/ms-marco-MiniLM-L-6-v2'
    )

    hybrid_retriever = HybridRerankerRetriever(
        first_retriever=vector_retriever,
        second_retriever=bm25_retriever,
        reranker=reranker,
        final_count=final_count,
    )
    return hybrid_retriever


def print_docs(
    docs_list: list[Document],
) -> list[Document]:
    """Print reranked documents.
    Args:
        docs_list (list[Document]): Reranked documents."""
    for index, doc_item in enumerate(docs_list, start=1):
        score_value = doc_item.metadata.get('rerank_score', 0.0)

        print(
            f'Rank {index}: '
            f'score={score_value:.4f}'
        )
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)

    return docs_list


if __name__ == '__main__':
    docs_list = build_docs()

    hybrid_retriever = build_retriever(
        docs_list=docs_list,
        candidate_count=5,
        final_count=3,
    )
    found_docs = hybrid_retriever.invoke(
        'Tell me about machine learning',
    )
    printed_docs = print_docs(
        docs_list=found_docs,
    )
