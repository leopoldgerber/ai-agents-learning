from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


def tokenize(text: str) -> set[str]:
    """Convert text into a simple set of normalized tokens."""
    return {
        word.strip('.,!?').lower()
        for word in text.split()
        if word.strip('.,!?')
    }


def build_docs() -> list[Document]:
    """Build sample documents."""
    return [
        Document(
            page_content='Python is used for machine learning.',
            metadata={
                'id': 'doc_1',
                'category': 'programming',
            },
        ),
        Document(
            page_content='Machine learning models learn from data.',
            metadata={
                'id': 'doc_2',
                'category': 'ml',
            },
        ),
        Document(
            page_content='JavaScript is used for web applications.',
            metadata={
                'id': 'doc_3',
                'category': 'web',
            },
        ),
    ]


class KeywordRetriever(BaseRetriever):
    """Retrieve documents by token overlap."""

    docs: list[Document]
    top_k: int = 2

    def _get_relevant_documents(
        self,
        query: str,
    ) -> list[Document]:
        """Implement keyword retrieval logic."""

        print('\n[KeywordRetriever]')
        print('_get_relevant_documents() started')
        print(f'Query: {query!r}')

        query_tokens = tokenize(query)
        scored_docs: list[tuple[int, Document]] = []

        for doc in self.docs:
            doc_tokens = tokenize(doc.page_content)

            matched_tokens = query_tokens & doc_tokens
            score = len(matched_tokens)

            print(
                f'Document {doc.metadata["id"]}: '
                f'matches={matched_tokens}, score={score}'
            )

            if score == 0:
                continue

            result_doc = Document(
                page_content=doc.page_content,
                metadata={
                    **doc.metadata,
                    'retrieval_score': score,
                    'retriever': 'keyword',
                },
            )

            scored_docs.append(
                (score, result_doc),
            )

        scored_docs.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            doc
            for _, doc in scored_docs[:self.top_k]
        ]


class CategoryRetriever(BaseRetriever):
    """Retrieve documents from a selected category."""

    docs: list[Document]
    category: str

    def _get_relevant_documents(
        self,
        query: str,
    ) -> list[Document]:
        """Implement category retrieval logic."""

        print('\n[CategoryRetriever]')
        print('_get_relevant_documents() started')
        print(f'Query received: {query!r}')
        print(f'Category filter: {self.category!r}')

        found_docs = []

        for doc in self.docs:
            if doc.metadata['category'] != self.category:
                continue

            result_doc = Document(
                page_content=doc.page_content,
                metadata={
                    **doc.metadata,
                    'retriever': 'category',
                },
            )

            found_docs.append(result_doc)

        return found_docs


def retrieval_pipeline(
    query: str,
    retriever: BaseRetriever,
) -> list[Document]:
    """Run any BaseRetriever-compatible retriever."""

    print('\n' + '=' * 60)
    print('[PIPELINE]')
    print(f'Retriever class: {type(retriever).__name__}')

    # The pipeline does not know HOW retrieval works.
    found_docs = retriever.invoke(query)

    print('\n[PIPELINE RESULT]')

    for index, doc in enumerate(found_docs, start=1):
        print(f'{index}. {doc.page_content}')
        print(f'   metadata={doc.metadata}')

    return found_docs


if __name__ == '__main__':
    docs = build_docs()

    keyword_retriever = KeywordRetriever(
        docs=docs,
        top_k=2,
    )

    category_retriever = CategoryRetriever(
        docs=docs,
        category='web',
    )

    retrieval_pipeline(
        query='Python machine learning',
        retriever=keyword_retriever,
    )

    retrieval_pipeline(
        query='Find information about web development',
        retriever=category_retriever,
    )
