import json

import requests


def parse_sse_event(event_lines: list[str]) -> dict[str, str]:
    """Parse one SSE event block into a dict.
    Args:
        event_lines (list[str]): Lines belonging to a single SSE event."""
    event_data: dict[str, str] = {}

    for line in event_lines:
        if line.startswith('id:'):
            event_data['id'] = line.replace('id:', '', 1).strip()
        elif line.startswith('event:'):
            event_data['event'] = line.replace('event:', '', 1).strip()
        elif line.startswith('data:'):
            event_data['data'] = line.replace('data:', '', 1).strip()

    return event_data


def read_sse_stream(url: str) -> None:
    """Read SSE stream and print parsed events.
    Args:
        url (str): SSE endpoint URL."""
    with requests.get(url, stream=True, timeout=30) as response:
        response.raise_for_status()

        buffer_lines: list[str] = []

        for raw_line in response.iter_lines(decode_unicode=True):
            if raw_line is None:
                continue

            if raw_line == '':
                if buffer_lines:
                    event_data = parse_sse_event(event_lines=buffer_lines)
                    if 'data' in event_data:
                        try:
                            payload = json.loads(event_data['data'])
                            event_data['data'] = json.dumps(
                                payload, ensure_ascii=False)
                        except json.JSONDecodeError:
                            pass
                    print(event_data)
                    buffer_lines = []
                continue

            buffer_lines.append(raw_line)


if __name__ == '__main__':
    sse_url = 'http://localhost:8000/stream'
    read_sse_stream(url=sse_url)
