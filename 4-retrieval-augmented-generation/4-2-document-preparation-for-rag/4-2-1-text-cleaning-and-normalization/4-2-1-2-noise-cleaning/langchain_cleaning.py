from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_community.document_loaders import (
    # PyMuPDFLoader,
    WebBaseLoader
)
# from langchain_text_splitters import TokenTextSplitter
import bs4


# 1. CREATE RUNNABLE LOADERS
class LoaderRunnable(RunnableLambda):
    def __init__(self, loader):
        super().__init__(lambda _: list(loader.lazy_load()))
        self.loader = loader


# load_pdf = LoaderRunnable(PyMuPDFLoader('docs/document.pdf'))
load_html = LoaderRunnable(
    WebBaseLoader(
        web_paths=(
            'https://docs.langchain.com/oss/python/langchain/overview',
        ),
        bs_kwargs={'parse_only': bs4.SoupStrainer(id='content')}
    )
)


# 2. CREATE RUNNABLE PROCESSORS
# The processing functions here are only placeholders
def clean_pdf_text(text: str) -> str:
    return text


def clean_html_text(text: str) -> str:
    return text


def normalize_text(text: str) -> str:
    return text.lower()


def apply_func_to_all_docs(func):
    def process_docs(docs):
        for doc in docs:
            doc.page_content = func(doc.page_content)
        return docs

    return process_docs


clean_pdf = RunnableLambda(apply_func_to_all_docs(clean_pdf_text))
clean_html = RunnableLambda(apply_func_to_all_docs(clean_html_text))
normalize_all = RunnableLambda(apply_func_to_all_docs(normalize_text))


# 4. CHAIN COMPOSITION
chain = (
    RunnableParallel(
        # pdf=load_pdf | clean_pdf,
        html=load_html | clean_html
    )
    | RunnableLambda(lambda x: x['pdf'] + x['html'])
    | normalize_all
)

# 5. INVOCATION
result = chain.invoke(None)

# 6. VIEW THE RESULT
for doc in result:
    print(doc.page_content[:50])
    print('Source:', doc.metadata['source'], '\n')
