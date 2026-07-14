import os
from typing import Literal, Optional

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class RAGState(MessagesState):
    """Store messages and explicit RAG workflow fields."""

    retrieved_docs: list[Document]
    grading_result: Optional[str]


class GradeDocuments(BaseModel):
    """Store structured document grading result."""

    binary_score: Literal['yes', 'no'] = Field(
        description='Whether documents are relevant to the question.',
    )


GRADE_PROMPT = ChatPromptTemplate.from_template(
    """
You are a document relevance grader.

User question:
{question}

Retrieved documents:
{documents}

Decide whether the documents contain useful information for answering
the question.

Relevant documents contain:
- A direct answer to the question
- Context needed to answer the question

Irrelevant documents:
- Discuss a different topic
- Contain only weakly related information
- Do not help answer the question
"""
)


def build_docs() -> list[Document]:
    """Build sample retrieved documents.
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
                'RAG improves LLM answers by using external '
                'knowledge from retrieval.'
            ),
            metadata={'source_id': 'doc_2'},
        ),
    ]
    return docs_list


def build_state(
    question: str,
    docs_list: list[Document],
) -> RAGState:
    """Build sample graph state for grading.
    Args:
        question (str): User question.
        docs_list (list[Document]): Retrieved documents."""
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
        grading_result=None,
    )
    return state


def extract_question(state: RAGState) -> str:
    """Extract first human question from graph state.
    Args:
        state (RAGState): Current graph state."""
    messages = state['messages']

    for message_item in messages:
        if getattr(message_item, 'type', '') == 'human':
            return str(message_item.content)

    return ''


def build_context(state: RAGState) -> str:
    """Build grading context from latest tool message.
    Args:
        state (RAGState): Current graph state."""
    messages = state['messages']

    for message_item in reversed(messages):
        if getattr(message_item, 'type', '') == 'tool':
            return str(message_item.content)

    docs_list = state.get('retrieved_docs', [])
    context_text = '\n\n'.join(
        doc_item.page_content
        for doc_item in docs_list
    )
    return context_text


def grade_docs(
    state: RAGState,
    model_name: str,
) -> dict[str, str]:
    """Grade retrieved documents with structured output.
    Args:
        state (RAGState): Current graph state.
        model_name (str): LLM model name."""
    question = extract_question(state=state)
    documents = build_context(state=state)

    if not question or not documents:
        return {'grading_result': 'generate'}

    grader_llm = ChatOpenAI(
        model=model_name,
        temperature=0,
    )
    grader = grader_llm.with_structured_output(GradeDocuments)

    prompt_value = GRADE_PROMPT.format(
        question=question,
        documents=documents,
    )
    result = grader.invoke(
        [
            {
                'role': 'user',
                'content': prompt_value,
            },
        ],
    )

    if result.binary_score == 'yes':
        return {'grading_result': 'generate'}

    return {'grading_result': 'rewrite'}


def decide_route(state: RAGState) -> Literal['generate', 'rewrite']:
    """Read grading route from graph state.
    Args:
        state (RAGState): Current graph state."""
    route_value = state.get('grading_result', 'generate')

    if route_value == 'rewrite':
        return 'rewrite'

    return 'generate'


def print_route(state_update: dict[str, str]) -> dict[str, str]:
    """Print grading route.
    Args:
        state_update (dict[str, str]): Grading node output."""
    print(f'Next route: {state_update["grading_result"]}')
    return state_update


if __name__ == '__main__':
    load_dotenv()

    model_name = os.getenv('OPENAI_MODEL', 'gpt-5')
    docs_list = build_docs()
    rag_state = build_state(
        question='What is LangGraph used for?',
        docs_list=docs_list,
    )
    state_update = grade_docs(
        state=rag_state,
        model_name=model_name,
    )
    printed_route = print_route(state_update=state_update)
