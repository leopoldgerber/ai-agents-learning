import numpy as np
from typing import List

from langchain_core.documents import Document
from langchain_core.vectorstores.in_memory import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    numerator = np.dot(v1, v2)
    denominator = np.linalg.norm(v1) * np.linalg.norm(v2)
    return float(numerator / denominator)


def dedupe_by_embedding(
    docs: List[Document],
    embedding_model,
    threshold: float = 0.95,
) -> List[Document]:
    # Create an in-memory vector store.
    vector_store = InMemoryVectorStore(embedding=embedding_model)
    kept_docs = []
    embeddings = []

    for doc in docs:
        text = doc.page_content.strip()

        if not text:
            continue

        emb = embedding_model.embed_documents([text])[0]

        if not embeddings:
            vector_store.add_documents([doc])
            embeddings.append(emb)
            kept_docs.append(doc)
            continue

        # Run a manual similarity search by comparing all embeddings.
        sims = [
            cosine_similarity(np.array(emb), np.array(existing_emb))
            for existing_emb in embeddings
        ]
        max_sim = max(sims)

        if max_sim < threshold:
            vector_store.add_documents([doc])
            embeddings.append(emb)
            kept_docs.append(doc)
        else:
            print(
                "Skipping duplicate by embedding: "
                f"'{text[:50]}...' with similarity = {max_sim}"
            )

    return kept_docs


# Usage example.
pages = [
    "abcd1234",
    (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ),
    (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXY"
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXY"
    ),
]

docs = []

for page_num, page_text in enumerate(pages, start=1):
    doc = Document(
        page_content=page_text,
        metadata={
            "source": "file_name",
            "page": page_num,
        },
    )
    docs.append(doc)

embed_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
)
filtered = dedupe_by_embedding(
    docs,
    embed_model,
    threshold=0.95,
)

print(filtered)
