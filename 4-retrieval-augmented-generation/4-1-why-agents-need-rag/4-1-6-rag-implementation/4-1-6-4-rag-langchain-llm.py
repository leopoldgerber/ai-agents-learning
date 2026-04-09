# pip install langchain langchain-openai langchain-core
# pip install langchain-community langchain-huggingface
# pip install sentence-transformers chromadb

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI


# Source text
documents_text = """
Machine learning is a branch of artificial intelligence that allows
computers to learn from data without explicit programming.

Neural networks are machine learning models inspired by the way the
human brain works. They consist of layers of interconnected nodes.

Deep learning is a subset of machine learning and uses multilayer
neural networks to solve complex tasks.

Supervised learning algorithms require labeled data, where each
example has a correct answer.

Clustering is an unsupervised learning method that groups similar
objects without prior labeling.
"""

# 1. Split text into fragments
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20,
    length_function=len
)
texts = text_splitter.split_text(documents_text)

# 2. Create embeddings
embeddings = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2'
)

# 3. Create vector store
vectorstore = Chroma.from_texts(
    texts=texts,
    embedding=embeddings,
    collection_name='ml_knowledge_llm'
)

# 4. Create retriever
retriever = vectorstore.as_retriever(
    search_type='similarity',
    search_kwargs={'k': 2}
)

# 5. Create LLM
llm = ChatOpenAI(
    model='gpt-3.5-turbo',
    temperature=0.7
)

# 6. Create prompt for answer generation
template = """Use the following context to answer the question.
If you do not know the answer, say so.
Answer in no more than three sentences.

Context: {context}

Question: {question}

Answer:"""

prompt = ChatPromptTemplate.from_template(template)


# 7. Function to format documents
def format_docs(docs):
    return '\n\n'.join(doc.page_content for doc in docs)


# 8. Create RAG chain with LCEL
rag_chain = (
    {
        'context': retriever | format_docs,
        'question': RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)


# 9. Use RAG with answer generation
def advanced_rag_lcel(query):
    """RAG with answer generation through LLM using LCEL."""
    answer = rag_chain.invoke(query)

    print(f'Query: {query}\n')
    print(f'Answer: {answer}\n')

    docs = retriever.invoke(query)
    print('Used sources:')
    for i, doc in enumerate(docs, 1):
        print(f'{i}. {doc.page_content[:100]}...')


# Example
advanced_rag_lcel(
    'Explain the difference between supervised and unsupervised learning'
)
