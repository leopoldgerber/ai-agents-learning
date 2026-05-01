from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def build_docs() -> list[Document]:
    """Build sample documents for indexing.
    Args:
        None (type): No arguments."""
    docs_list = [
        Document(
            page_content='How to cook pasta with tomato sauce',
            metadata={'source': 'recipe_notes', 'topic': 'cooking'},
        ),
        Document(
            page_content='How to train a retrieval system with embeddings',
            metadata={'source': 'rag_notes', 'topic': 'rag'},
        ),
        Document(
            page_content='How to boil noodles and prepare a quick dinner',
            metadata={'source': 'kitchen_book', 'topic': 'cooking'},
        ),
    ]
    return docs_list


def build_model(model_name: str) -> HuggingFaceEmbeddings:
    """Build embedding model.
    Args:
        model_name (str): Name of embedding model."""
    embed_model = HuggingFaceEmbeddings(model_name=model_name)
    return embed_model


def build_index(
    docs_list: list[Document],
    embed_model: HuggingFaceEmbeddings,
) -> FAISS:
    """Build vector index from documents.
    Args:
        docs_list (list[Document]): Documents for indexing.
        embed_model (HuggingFaceEmbeddings): Embedding model."""
    vector_store = FAISS.from_documents(docs_list, embed_model)
    return vector_store


def search_index(
    vector_store: FAISS,
    query: str,
    top_k: int,
) -> list[Document]:
    """Search similar documents in index.
    Args:
        vector_store (FAISS): Built vector index.
        query (str): Search query.
        top_k (int): Number of results."""
    found_docs = vector_store.similarity_search(query, k=top_k)
    return found_docs


def print_docs(found_docs: list[Document]) -> list[Document]:
    """Print found documents with metadata.
    Args:
        found_docs (list[Document]): Search results."""
    for index, doc_item in enumerate(found_docs, start=1):
        print(f'Result {index}:')
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)
    return found_docs


if __name__ == '__main__':
    docs_list = build_docs()
    embed_model = build_model(model_name='all-MiniLM-L6-v2')
    vector_store = build_index(
        docs_list=docs_list,
        embed_model=embed_model,
    )
    found_docs = search_index(
        vector_store=vector_store,
        query='pasta recipe',
        top_k=2,
    )
    printed_docs = print_docs(found_docs=found_docs)
