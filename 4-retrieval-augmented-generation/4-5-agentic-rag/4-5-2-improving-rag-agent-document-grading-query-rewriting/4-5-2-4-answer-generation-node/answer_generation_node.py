import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState


class RAGState(MessagesState):
    """Store messages and explicit RAG workflow fields."""

    retrieved_docs: list[Document]
    grading_result: Optional[str]


ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """
Answer the user question using only the provided context.

Question:
{question}

Knowledge base context:
{context}

Rules:
1. Use only information from the context.
2. If the context does not contain the answer, say that honestly.
3. Answer briefly and directly.
"""
)


def build_docs() -> list[Document]:
    """Build sample relevant documents.
    Args:
        None: No arguments."""
    docs_list = [
        Document(
            page_content=(
                'LangGraph helps build cyclic agent workflows '
                'with conditional transitions.'
            ),
            metadata={'source_id': 'doc_1'},
        ),
        Document(
            page_content=(
                'Agentic RAG can decide whether retrieval is needed '
                'and can route workflow steps.'
            ),
            metadata={'source_id': 'doc_2'},
        ),
    ]
    return docs_list


def build_state(
    question: str,
    docs_list: list[Document],
) -> RAGState:
    """Build sample state for answer generation.
    Args:
        question (str): User question.
        docs_list (list[Document]): Retrieved relevant documents."""
    context_text = '\n\n'.join(
        doc_item.page_content
        for doc_item in docs_list
    )

    state = RAGState(
        messages=[
            HumanMessage(content=question),
            ToolMessage(
                content=context_text,
                tool_call_id='demo_tool_call',
                name='knowledge_base_search',
            ),
        ],
        retrieved_docs=docs_list,
        grading_result='generate',
    )
    return state


def extract_question(state: RAGState) -> str:
    """Extract latest human question from state.
    Args:
        state (RAGState): Current graph state."""
    messages = state['messages']
    question = ''

    for message_item in messages:
        if getattr(message_item, 'type', '') == 'human':
            question = str(message_item.content)

    return question


def extract_context(state: RAGState) -> str:
    """Extract latest tool context from state.
    Args:
        state (RAGState): Current graph state."""
    messages = state['messages']
    context = ''

    for message_item in messages:
        if getattr(message_item, 'type', '') == 'tool':
            context = str(message_item.content)

    if context:
        return context

    docs_list = state.get('retrieved_docs', [])
    context_text = '\n\n'.join(
        doc_item.page_content
        for doc_item in docs_list
    )
    return context_text


def generate_answer(
    state: RAGState,
    model_name: str,
) -> dict[str, list[object]]:
    """Generate final answer from question and context.
    Args:
        state (RAGState): Current graph state.
        model_name (str): LLM model name."""
    question = extract_question(state=state)
    context = extract_context(state=state)

    generator_llm = ChatOpenAI(
        model=model_name,
        temperature=0,
    )
    prompt_value = ANSWER_PROMPT.format(
        question=question,
        context=context,
    )
    response = generator_llm.invoke(
        [
            {
                'role': 'user',
                'content': prompt_value,
            },
        ],
    )

    return {'messages': [response]}


def print_answer(
    state_update: dict[str, list[object]],
) -> dict[str, list[object]]:
    """Print generated answer.
    Args:
        state_update (dict[str, list[object]]): Generate node output."""
    messages = state_update.get('messages', [])

    for message_item in messages:
        print(message_item.content)

    return state_update


if __name__ == '__main__':
    load_dotenv()

    model_name = os.getenv('OPENAI_MODEL', 'gpt-5')
    docs_list = build_docs()
    rag_state = build_state(
        question='What is LangGraph used for?',
        docs_list=docs_list,
    )
    state_update = generate_answer(
        state=rag_state,
        model_name=model_name,
    )
    printed_answer = print_answer(state_update=state_update)
