import json
import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class RAGState(MessagesState):
    """Store messages and retrieved documents for citation."""

    retrieved_docs: list[Document]
    grading_result: Optional[str]


class Claim(BaseModel):
    """Store one verifiable answer claim with source ids."""

    claim: str = Field(description='Verifiable answer claim.')
    source_ids: list[str] = Field(description='Source ids for the claim.')


class AnswerWithCitations(BaseModel):
    """Store final answer text and cited claims."""

    answer: str = Field(description='Short answer for the user.')
    claims: list[Claim] = Field(description='Claims with source ids.')


ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """
Answer the user question using only the provided context.

Question:
{question}

Context:
{context}

Rules:
- source_ids may contain only source ids shown in square brackets
- Every claim should refer to concrete sources
- If the answer is missing from context, return an empty claims list
- Answer briefly and directly

Return the response using the requested structured output format.
"""
)


def build_docs() -> list[Document]:
    """Build sample retrieved documents with source ids.
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
                'knowledge retrieved from documents.'
            ),
            metadata={'source_id': 'doc_2'},
        ),
    ]
    return docs_list


def build_state(
    question: str,
    docs_list: list[Document],
) -> RAGState:
    """Build sample graph state for citation.
    Args:
        question (str): User question.
        docs_list (list[Document]): Retrieved documents."""
    state = RAGState(
        messages=[
            HumanMessage(content=question),
        ],
        retrieved_docs=docs_list,
        grading_result='generate',
    )
    return state


def extract_question(state: RAGState) -> str:
    """Extract first human question from state.
    Args:
        state (RAGState): Current graph state."""
    messages = state['messages']

    for message_item in messages:
        if getattr(message_item, 'type', '') == 'human':
            return str(message_item.content)

    return ''


def format_documents(docs_list: list[Document]) -> str:
    """Format documents with source ids for citation.
    Args:
        docs_list (list[Document]): Documents to format."""
    formatted_items = []

    for doc_item in docs_list:
        source_id = str(doc_item.metadata.get('source_id', 'unknown'))
        content = doc_item.page_content.strip()
        formatted_items.append(f'[{source_id}]\n{content}')

    context_text = '\n\n'.join(formatted_items)
    return context_text


def get_sources(docs_list: list[Document]) -> set[str]:
    """Get available source ids from documents.
    Args:
        docs_list (list[Document]): Documents with metadata."""
    source_ids = {
        str(doc_item.metadata.get('source_id', 'unknown'))
        for doc_item in docs_list
    }
    return source_ids


def validate_citations(
    answer_data: AnswerWithCitations,
    available_ids: set[str],
) -> AnswerWithCitations:
    """Validate that answer uses only available source ids.
    Args:
        answer_data (AnswerWithCitations): Structured answer object.
        available_ids (set[str]): Allowed source ids."""
    for claim_item in answer_data.claims:
        for source_id in claim_item.source_ids:
            if source_id not in available_ids:
                raise ValueError(f'Invalid source id: {source_id}')

    return answer_data


def calculate_rate(claims_list: list[Claim]) -> float:
    """Calculate citation rate for answer claims.
    Args:
        claims_list (list[Claim]): Claims from structured answer."""
    if not claims_list:
        return 0.0

    cited_count = sum(
        1
        for claim_item in claims_list
        if claim_item.source_ids
    )
    citation_rate = cited_count / len(claims_list)
    return citation_rate


def build_empty() -> dict[str, object]:
    """Build empty cited response.
    Args:
        None: No arguments."""
    empty_response = {
        'answer': (
            'I did not find enough information in the retrieved '
            'documents to answer the question.'
        ),
        'claims': [],
    }
    return empty_response


def generate_answer(
    state: RAGState,
    model_name: str,
) -> dict[str, list[AIMessage]]:
    """Generate answer with structured citations.
    Args:
        state (RAGState): Current graph state.
        model_name (str): LLM model name."""
    question = extract_question(state=state)
    docs_list = state.get('retrieved_docs', [])

    if not docs_list:
        empty_response = build_empty()
        response_json = json.dumps(
            empty_response,
            ensure_ascii=False,
        )
        return {'messages': [AIMessage(content=response_json)]}

    context_text = format_documents(docs_list=docs_list)
    available_ids = get_sources(docs_list=docs_list)

    llm_model = ChatOpenAI(
        model=model_name,
        temperature=0,
    )
    structured_model = llm_model.with_structured_output(
        AnswerWithCitations
    )
    prompt_value = ANSWER_PROMPT.format(
        question=question,
        context=context_text,
    )
    answer_data = structured_model.invoke(prompt_value)
    validated_data = validate_citations(
        answer_data=answer_data,
        available_ids=available_ids,
    )

    citation_rate = calculate_rate(claims_list=validated_data.claims)
    response_data = validated_data.model_dump()
    response_data['citation_rate'] = citation_rate

    response_json = json.dumps(
        response_data,
        ensure_ascii=False,
    )
    return {'messages': [AIMessage(content=response_json)]}


def print_answer(
    state_update: dict[str, list[AIMessage]],
) -> dict[str, list[AIMessage]]:
    """Print structured cited answer.
    Args:
        state_update (dict[str, list[AIMessage]]): Generate node output."""
    messages = state_update.get('messages', [])

    for message_item in messages:
        result_data = json.loads(str(message_item.content))

        print('Answer:')
        print(result_data.get('answer', ''))
        print('')

        print('Claims:')
        for claim_item in result_data.get('claims', []):
            print(claim_item.get('claim', ''))
            print(claim_item.get('source_ids', []))

        print('')
        print(f'Citation rate: {result_data.get("citation_rate", 0.0):.0%}')

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
