import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState


class RAGState(MessagesState):
    """Store messages and explicit RAG workflow fields."""

    retrieved_docs: list[Document]
    grading_result: Optional[str]


REWRITE_PROMPT = ChatPromptTemplate.from_template(
    """
You are an expert in rewriting search queries.

Original user question:
{question}

This question did not produce good retrieval results.

Rewrite it to improve knowledge-base search:
- Make the question more specific
- Add synonyms or alternative formulations
- Split complex intent into clearer parts
- Change word order if it helps matching

Return only the rewritten question. Do not add explanations.
"""
)


def build_state(question: str) -> RAGState:
    """Build sample graph state with user question.
    Args:
        question (str): Original user question."""
    state = RAGState(
        messages=[
            HumanMessage(content=question),
        ],
        retrieved_docs=[],
        grading_result='rewrite',
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


def rewrite_query(
    state: RAGState,
    model_name: str,
) -> dict[str, list[HumanMessage]]:
    """Rewrite user query for better retrieval.
    Args:
        state (RAGState): Current graph state.
        model_name (str): LLM model name."""
    question = extract_question(state=state)

    if not question:
        return {'messages': []}

    rewrite_llm = ChatOpenAI(
        model=model_name,
        temperature=0.3,
    )
    prompt_value = REWRITE_PROMPT.format(question=question)
    rewritten = rewrite_llm.invoke(
        [
            {
                'role': 'user',
                'content': prompt_value,
            },
        ],
    )

    rewritten_message = HumanMessage(content=str(rewritten.content))
    return {'messages': [rewritten_message]}


def print_rewrite(
    state_update: dict[str, list[HumanMessage]],
) -> dict[str, list[HumanMessage]]:
    """Print rewritten query from state update.
    Args:
        state_update (dict[str, list[HumanMessage]]): Rewrite output."""
    messages = state_update.get('messages', [])

    for message_item in messages:
        print(message_item.content)

    return state_update


if __name__ == '__main__':
    load_dotenv()

    model_name = os.getenv('OPENAI_MODEL', 'gpt-5')
    rag_state = build_state(question='Tell me about graph')
    state_update = rewrite_query(
        state=rag_state,
        model_name=model_name,
    )
    printed_rewrite = print_rewrite(state_update=state_update)
