import os
from typing import Any

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool, create_retriever_tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition


def build_docs() -> list[Document]:
    """Build sample knowledge base documents.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content=(
                'LangChain is a framework for building applications '
                'based on large language models.'
            ),
            metadata={'source_id': 'doc_1'},
        ),
        Document(
            page_content=(
                'LangGraph makes it possible to build cyclic agent '
                'workflows with conditional transitions.'
            ),
            metadata={'source_id': 'doc_2'},
        ),
        Document(
            page_content=(
                'RAG improves LLM accuracy by adding external '
                'knowledge through retrieval.'
            ),
            metadata={'source_id': 'doc_3'},
        ),
        Document(
            page_content=(
                'Python is a popular language for machine learning '
                'and data science.'
            ),
            metadata={'source_id': 'doc_4'},
        ),
    ]
    return docs_list


def build_tool(
    docs_list: list[Document],
    candidate_count: int,
) -> BaseTool:
    """Build retriever tool from vector store.
    Args:
        docs_list (list[Document]): Documents for knowledge base.
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


def call_agent(
    state: MessagesState,
    llm_with_tools: Runnable,
) -> dict[str, list[Any]]:
    """Call agent node with message state.
    Args:
        state (MessagesState): Current graph message state.
        llm_with_tools (Runnable): LLM bound to available tools."""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)

    return {'messages': [response]}


def build_graph(
    tools_list: list[BaseTool],
    llm_with_tools: Runnable,
) -> Any:
    """Build LangGraph agent workflow.
    Args:
        tools_list (list[BaseTool]): Tools for ToolNode.
        llm_with_tools (Runnable): LLM bound to available tools."""
    tool_node = ToolNode(tools_list)
    workflow = StateGraph(MessagesState)

    def agent_node(state: MessagesState) -> dict[str, list[Any]]:
        """Run agent node inside workflow.
        Args:
            state (MessagesState): Current graph message state."""
        agent_response = call_agent(
            state=state,
            llm_with_tools=llm_with_tools,
        )
        return agent_response

    workflow.add_node('agent', agent_node)
    workflow.add_node('tools', tool_node)

    workflow.add_edge(START, 'agent')
    workflow.add_conditional_edges(
        'agent',
        tools_condition,
        {
            'tools': 'tools',
            END: END,
        },
    )
    workflow.add_edge('tools', 'agent')

    graph_app = workflow.compile()
    return graph_app


def run_query(
    graph_app: Any,
    query: str,
) -> dict[str, Any]:
    """Run query through compiled graph.
    Args:
        graph_app (Any): Compiled LangGraph workflow.
        query (str): User query."""
    response = graph_app.invoke(
        {
            'messages': [
                HumanMessage(content=query),
            ],
        },
    )
    return response


def print_answer(
    response: dict[str, Any],
) -> dict[str, Any]:
    """Print final graph answer.
    Args:
        response (dict[str, Any]): Graph response with messages."""
    final_message = response['messages'][-1]
    print(final_message.content)

    return response


if __name__ == '__main__':
    docs_list = build_docs()
    retriever_tool = build_tool(
        docs_list=docs_list,
        candidate_count=3,
    )
    tools_list = [retriever_tool]

    llm_with_tools = build_model(tools_list=tools_list)
    graph_app = build_graph(
        tools_list=tools_list,
        llm_with_tools=llm_with_tools,
    )

    search_response = run_query(
        graph_app=graph_app,
        query='What is LangGraph?',
    )
    printed_search = print_answer(response=search_response)

    direct_response = run_query(
        graph_app=graph_app,
        query='Hello, how are you?',
    )
    printed_direct = print_answer(response=direct_response)
