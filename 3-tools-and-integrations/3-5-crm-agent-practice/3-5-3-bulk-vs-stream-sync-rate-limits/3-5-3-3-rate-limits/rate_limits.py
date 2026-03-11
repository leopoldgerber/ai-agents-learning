import time
from typing import Any

import requests


class RateLimitError(Exception):
    """Represent rate-limit failure.
    Args:
        None: No arguments."""


def build_headers(access_token: str) -> dict[str, str]:
    """Build request headers.
    Args:
        access_token (str): CRM access token."""
    return {'Authorization': f'Bearer {access_token}'}


def read_retry_after(response: requests.Response) -> int:
    """Read retry delay from response headers.
    Args:
        response (requests.Response): CRM API response."""
    retry_value = response.headers.get('Retry-After', '5')
    return int(retry_value)


def send_request(
    api_url: str,
    access_token: str,
    params: dict[str, Any],
    timeout_sec: int,
) -> requests.Response:
    """Send CRM request.
    Args:
        api_url (str): CRM endpoint URL.
        access_token (str): CRM access token.
        params (dict[str, Any]): Query parameters.
        timeout_sec (int): Request timeout in seconds."""
    headers = build_headers(access_token=access_token)
    response = requests.get(
        api_url,
        headers=headers,
        params=params,
        timeout=timeout_sec,
    )
    return response


def fetch_with_retry(
    api_url: str,
    access_token: str,
    params: dict[str, Any],
    timeout_sec: int,
    max_attempts: int,
) -> dict[str, Any]:
    """Fetch CRM data with rate-limit handling.
    Args:
        api_url (str): CRM endpoint URL.
        access_token (str): CRM access token.
        params (dict[str, Any]): Query parameters.
        timeout_sec (int): Request timeout in seconds.
        max_attempts (int): Maximum retry attempts."""
    attempt_index = 0

    while attempt_index < max_attempts:
        response = send_request(
            api_url=api_url,
            access_token=access_token,
            params=params,
            timeout_sec=timeout_sec,
        )

        if response.status_code == 429:
            wait_sec = read_retry_after(response=response)
            time.sleep(wait_sec)
            attempt_index += 1
            continue

        response.raise_for_status()
        return response.json()

    raise RateLimitError('Maximum retry attempts reached')


if __name__ == '__main__':
    crm_api_url = 'https://crm.example.com/api/v1/leads'
    crm_access_token = 'YOUR_ACCESS_TOKEN'
    request_params = {'limit': 100}

    crm_result = fetch_with_retry(
        api_url=crm_api_url,
        access_token=crm_access_token,
        params=request_params,
        timeout_sec=30,
        max_attempts=5,
    )
    print(crm_result)
