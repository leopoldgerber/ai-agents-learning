from typing import List
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


model = SentenceTransformer('all-MiniLM-L6-v2')


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Convert texts into embeddings.
    Args:
        texts (List[str]): List of input texts."""
    return model.encode(texts)


def semantic_search(documents: List[str], query: str) -> List[str]:
    """Return documents ranked by semantic similarity.
    Args:
        documents (List[str]): List of documents.
        query (str): User query."""
    doc_embeddings = embed_texts(documents)
    query_embedding = embed_texts([query])[0]

    similarities = cosine_similarity(
        [query_embedding],
        doc_embeddings
    )[0]

    ranked_indices = similarities.argsort()[::-1]

    return [documents[i] for i in ranked_indices]


if __name__ == "__main__":
    documents = [
        "AI research is evolving quickly",
        "Machine learning improves predictions",
        "Deep learning in artificial intelligence",
        "New robotics technologies"
    ]

    query = "AI systems"

    results = semantic_search(documents, query)

    for result in results:
        print(result)
