from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


def build_docs() -> list[Document]:
    """Build sample documents for retrieval.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content=(
                'Python is commonly used for machine learning.'
            ),
            metadata={
                'id': 'doc_1',
                'category': 'programming',
            },
        ),
        Document(
            page_content=(
                'Machine learning models learn patterns from data.'
            ),
            metadata={
                'id': 'doc_2',
                'category': 'ml',
            },
        ),
        Document(
            page_content=(
                'JavaScript is commonly used in web applications.'
            ),
            metadata={
                'id': 'doc_3',
                'category': 'web',
            },
        ),
    ]
    return docs_list


class KeywordRetriever(BaseRetriever):
    """Retrieve documents by simple token overlap."""

    docs_list: list[Document]
    top_k: int = 3

    def _get_relevant_documents(
        self,
        query: str,
    ) -> list[Document]:
        """Retrieve documents for input query.
        Args:
            query (str): User search query."""
        query_tokens = set(query.lower().split())
        scored_docs = []

        for doc_item in self.docs_list:
            doc_tokens = set(
                doc_item.page_content.lower().split()
            )
            overlap_count = len(query_tokens & doc_tokens)
            scored_docs.append(
                (overlap_count, doc_item),
            )

        scored_docs.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        found_docs = [
            doc_item
            for score_value, doc_item in scored_docs[:self.top_k]
            if score_value > 0
        ]
        return found_docs


def print_docs(
    docs_list: list[Document],
) -> list[Document]:
    """Print retrieved documents.
    Args:
        docs_list (list[Document]): Retrieved documents."""
    for index, doc_item in enumerate(docs_list, start=1):
        print(f'Result {index}:')
        print(doc_item.page_content)
        print(doc_item.metadata)
        print('-' * 40)

    return docs_list


if __name__ == '__main__':
    docs_list = build_docs()

    retriever = KeywordRetriever(
        docs_list=docs_list,
        top_k=2,
    )

    found_docs = retriever.invoke(
        'Python machine learning',
    )
    printed_docs = print_docs(
        docs_list=found_docs,
    )
