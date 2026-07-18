import json
import logging
import os
from collections.abc import Iterator
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv('OPENAI_MODEL', 'gpt-5')


class StreamQuery(BaseModel):
    """Store streaming request payload."""

    question: str = Field(min_length=1, max_length=1000)


def build_agent() -> Any:
    """Build streaming LangChain agent.
    Args:
        None: No arguments."""
    model = ChatOpenAI(
        model=MODEL_NAME,
        streaming=True,
        temperature=0,
    )
    agent = create_agent(model=model)

    return agent


def build_event(
    event_type: str,
    content: str,
) -> str:
    """Build Server-Sent Event line.
    Args:
        event_type (str): Event type name.
        content (str): Event content."""
    event_data = {
        'type': event_type,
        'content': content,
    }
    event_text = json.dumps(
        event_data,
        ensure_ascii=False,
    )

    return f'data: {event_text}\n\n'


def stream_agent_tokens(
    agent: Any,
    question: str,
) -> Iterator[str]:
    """Stream agent answer tokens as SSE events.
    Args:
        agent (Any): Streaming LangChain agent.
        question (str): User question."""
    input_data = {
        'messages': [
            {
                'role': 'user',
                'content': question,
            },
        ],
    }

    try:
        for token, metadata in agent.stream(
            input_data,
            stream_mode='messages',
        ):
            blocks = getattr(token, 'content_blocks', [])

            if not blocks or hasattr(token, 'tool_call_id'):
                continue

            block = blocks[0]

            if block.get('type') != 'text':
                continue

            yield build_event(
                event_type='token',
                content=str(block.get('text', '')),
            )

        yield build_event(
            event_type='done',
            content='',
        )

    except Exception as error:
        logger.error('Streaming generation failed', exc_info=True)
        yield build_event(
            event_type='error',
            content=str(error),
        )


def create_api() -> FastAPI:
    """Create FastAPI application with streaming endpoint.
    Args:
        None: No arguments."""
    agent = build_agent()
    app = FastAPI(title='LangChain Agent Streaming API')

    @app.post('/ask_stream')
    def ask_stream(query: StreamQuery) -> StreamingResponse:
        """Stream answer tokens through SSE.
        Args:
            query (StreamQuery): User question payload."""
        logger.info('Received streaming query: %s', query.question)

        return StreamingResponse(
            stream_agent_tokens(
                agent=agent,
                question=query.question,
            ),
            media_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            },
        )

    @app.get('/health')
    def health_check() -> dict[str, str]:
        """Return service health status.
        Args:
            None: No arguments."""
        return {'status': 'healthy'}

    return app


def print_graph_stream(
    graph_app: Any,
    question: str,
) -> str:
    """Print LangGraph message stream.
    Args:
        graph_app (Any): Compiled LangGraph application.
        question (str): User question."""
    input_data = {
        'messages': [
            HumanMessage(content=question),
        ],
    }
    answer_parts = []

    for chunk, metadata in graph_app.stream(
        input_data,
        stream_mode='messages',
    ):
        content = getattr(chunk, 'content', '')
        tool_calls = getattr(chunk, 'tool_calls', [])

        if not content or tool_calls:
            continue

        print(content, end='', flush=True)
        answer_parts.append(str(content))

    print('')
    return ''.join(answer_parts)


app = create_api()


if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
    )
