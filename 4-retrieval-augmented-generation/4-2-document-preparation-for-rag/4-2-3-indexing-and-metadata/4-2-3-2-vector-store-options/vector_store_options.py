from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma, FAISS


def build_docs() -> list[Document]:
    """Build sample documents for vector stores.
    Args:
        None (type): No arguments."""
    docs_list = [
        Document(
            page_content='Pasta recipe with tomato and basil',
            metadata={'source': 'cookbook', 'topic': 'cooking'},
        ),
        Document(
            page_content='Vector databases store embeddings efficiently',
            metadata={'source': 'rag_book', 'topic': 'rag'},
        ),
        Document(
            page_content='How similarity search works in retrieval systems',
            metadata={'source': 'ml_notes', 'topic': 'rag'},
        ),
    ]
    return docs_list


def build_model(model_name: str) -> HuggingFaceEmbeddings:
    """Build embedding model.
    Args:
        model_name (str): Name of embedding model."""
    embed_model = HuggingFaceEmbeddings(model_name=model_name)
    return embed_model


def build_faiss_store(
    docs_list: list[Document],
    embed_model: HuggingFaceEmbeddings,
) -> FAISS:
    """Build FAISS vector store.
    Args:
        docs_list (list[Document]): Documents for indexing.
        embed_model (HuggingFaceEmbeddings): Embedding model."""
    vector_store = FAISS.from_documents(docs_list, embed_model)
    return vector_store


def build_chroma_store(
    docs_list: list[Document],
    embed_model: HuggingFaceEmbeddings,
) -> Chroma:
    """Build Chroma vector store.
    Args:
        docs_list (list[Document]): Documents for indexing.
        embed_model (HuggingFaceEmbeddings): Embedding model."""
    vector_store = Chroma.from_documents(docs_list, embed_model)
    return vector_store


def print_search(
    store_name: str,
    found_docs: list[Document],
) -> list[Document]:
    """Print search results for one vector store.
    Args:
        store_name (str): Name of vector store.
        found_docs (list[Document]): Retrieved documents."""
    print(store_name)

    for index, doc_item in enumerate(found_docs, start=1):
        print(f'Result {index}:')
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)

    return found_docs


if __name__ == '__main__':
    docs_list = build_docs()
    embed_model = build_model(model_name='all-MiniLM-L6-v2')

    faiss_store = build_faiss_store(
        docs_list=docs_list,
        embed_model=embed_model,
    )
    chroma_store = build_chroma_store(
        docs_list=docs_list,
        embed_model=embed_model,
    )

    faiss_docs = faiss_store.similarity_search('retrieval search', k=2)
    printed_faiss = print_search(
        store_name='FAISS results',
        found_docs=faiss_docs,
    )

    chroma_docs = chroma_store.similarity_search('retrieval search', k=2)
    printed_chroma = print_search(
        store_name='Chroma results',
        found_docs=chroma_docs,
    )
