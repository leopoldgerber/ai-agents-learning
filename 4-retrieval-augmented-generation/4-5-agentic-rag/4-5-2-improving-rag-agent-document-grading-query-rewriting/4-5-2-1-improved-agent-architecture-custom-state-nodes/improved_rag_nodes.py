import os
from typing import Optional

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import ToolMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool, create_retriever_tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState


class RAGState(MessagesState):
    """Store messages and explicit RAG workflow fields."""

    retrieved_docs: list[Document]
    grading_result: Optional[str]


def build_docs() -> list[Document]:
    """Build sample documents for the knowledge base.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content=(
                'LangChain is a framework for building LLM '
                'applications.'
            ),
            metadata={'source_id': 'doc_1'},
        ),
        Document(
            page_content=(
                'LangGraph helps build cyclic agent workflows '
                'with conditional transitions.'
            ),
            metadata={'source_id': 'doc_2'},
        ),
        Document(
            page_content=(
                'RAG improves LLM accuracy through external '
                'knowledge retrieval.'
            ),
            metadata={'source_id': 'doc_3'},
        ),
        Document(
            page_content=(
                'Python is popular for machine learning and '
                'data science.'
            ),
            metadata={'source_id': 'doc_4'},
        ),
    ]
    return docs_list


def build_retriever(
    docs_list: list[Document],
    candidate_count: int,
) -> Runnable:
    """Build vector retriever from documents.
    Args:
        docs_list (list[Document]): Documents for vector store.
        candidate_count (int): Number of retrieved documents."""
    embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2',
    )
    vector_store = FAISS.from_documents(
        documents=docs_list,
        embedding=embeddings,
    )
    retriever = vector_store.as_retriever(
        search_kwargs={'k': candidate_count},
    )

    return retriever


def build_tool(
    retriever: Runnable,
) -> BaseTool:
    """Build retriever tool for the agent.
    Args:
        retriever (Runnable): Retriever used by the tool."""
    retriever_tool = create_retriever_tool(
        retriever,
        name='knowledge_base_search',
        description=(
            'Search information about LangChain, LangGraph, '
            'and RAG systems. Use this tool when knowledge '
            'base information is needed.'
        ),
    )
    return retriever_tool


def build_model(
    tools_list: list[BaseTool],
) -> Runnable:
    """Build LLM with bound tools.
    Args:
        tools_list (list[BaseTool]): Tools available to the LLM."""
    load_dotenv()

    model_name = os.getenv('OPENAI_MODEL', 'gpt-5')
    llm_model = ChatOpenAI(
        model_name=model_name,
        temperature=0,
    )
    llm_with_tools = llm_model.bind_tools(tools_list)

    return llm_with_tools


def agent_node(
    state: RAGState,
    llm_with_tools: Runnable,
) -> dict[str, list[object]]:
    """Run agent node and return LLM response.
    Args:
        state (RAGState): Current graph state.
        llm_with_tools (Runnable): LLM bound to retriever tools."""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)

    return {'messages': [response]}


def find_tool_calls(state: RAGState) -> list[dict[str, object]]:
    """Find latest tool calls in message history.
    Args:
        state (RAGState): Current graph state."""
    messages = state['messages']

    for message_item in reversed(messages):
        has_calls = hasattr(message_item, 'tool_calls')
        if has_calls and message_item.tool_calls:
            return list(message_item.tool_calls)

    return []


def retrieve_node(
    state: RAGState,
    retriever: Runnable,
) -> dict[str, list[object]]:
    """Run retrieval and store tool messages plus documents.
    Args:
        state (RAGState): Current graph state.
        retriever (Runnable): Retriever for knowledge base search."""
    tool_calls = find_tool_calls(state=state)

    if not tool_calls:
        return {
            'messages': [],
            'retrieved_docs': [],
        }

    tool_messages = []
    retrieved_docs = []

    for tool_call in tool_calls:
        tool_name = str(tool_call.get('name', ''))

        if tool_name != 'knowledge_base_search':
            continue

        tool_args = tool_call.get('args', {})
        query = str(tool_args.get('query', ''))
        docs_list = retriever.invoke(query)
        retrieved_docs.extend(docs_list)

        content = '\n\n'.join(
            doc_item.page_content
            for doc_item in docs_list
        )
        tool_message = ToolMessage(
            content=content,
            tool_call_id=str(tool_call.get('id', '')),
            name=tool_name,
        )
        tool_messages.append(tool_message)

    return {
        'messages': tool_messages,
        'retrieved_docs': retrieved_docs,
    }


def summarize_state(state_update: dict[str, list[object]]) -> dict[str, int]:
    """Summarize node output for debugging.
    Args:
        state_update (dict[str, list[object]]): Node output values."""
    summary = {
        'message_count': len(state_update.get('messages', [])),
        'retrieved_count': len(state_update.get('retrieved_docs', [])),
    }
    return summary


if __name__ == '__main__':
    docs_list = build_docs()
    retriever = build_retriever(
        docs_list=docs_list,
        candidate_count=3,
    )
    retriever_tool = build_tool(retriever=retriever)
    llm_with_tools = build_model(tools_list=[retriever_tool])

    initial_state = RAGState(
        messages=[],
        retrieved_docs=[],
        grading_result=None,
    )
    agent_update = agent_node(
        state=initial_state,
        llm_with_tools=llm_with_tools,
    )
    state_summary = summarize_state(state_update=agent_update)
    print(state_summary)
