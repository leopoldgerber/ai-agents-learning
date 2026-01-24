from typing import Any

import requests


def send_request(url: str, payload: dict[str, Any]) -> requests.Response:
    """Send a POST request with JSON payload.
    Args:
        url (str): Target endpoint URL.
        payload (dict[str, Any]): JSON payload."""
    return requests.post(url, json=payload, timeout=10)


def parse_result(response: requests.Response) -> dict[str, Any]:
    """Parse response JSON or fallback to plain text.
    Args:
        response (requests.Response): HTTP response."""
    try:
        return response.json()
    except ValueError:
        return {'raw_text': response.text}


def run_agent(server_url: str) -> list[dict[str, Any]]:
    """Run a minimal agent that tests valid and invalid payloads.
    Args:
        server_url (str): Base server URL."""
    endpoint = f'{server_url}/validate'

    valid_payload = {
        'user_id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
    invalid_payload = {'user_id': -1, 'name': '', 'extra': 'not allowed'}

    results: list[dict[str, Any]] = []

    for payload in [valid_payload, invalid_payload]:
        response = send_request(url=endpoint, payload=payload)
        result = parse_result(response=response)
        results.append({'status_code': response.status_code, 'body': result})

    return results


if __name__ == '__main__':
    results = run_agent(server_url='http://localhost:8000')
    for item in results:
        print(item)
