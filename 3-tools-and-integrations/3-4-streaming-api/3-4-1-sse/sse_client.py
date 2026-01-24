import requests


def consume_sse_stream(url: str) -> None:
    """Consume SSE stream and print raw events.
    Args:
        url (str): SSE endpoint URL."""
    with requests.get(url, stream=True, timeout=30) as response:
        response.raise_for_status()

        for raw_line in response.iter_lines(decode_unicode=True):
            if raw_line:
                print(raw_line)


if __name__ == '__main__':
    sse_url = 'http://localhost:8000/stream'
    consume_sse_stream(url=sse_url)
