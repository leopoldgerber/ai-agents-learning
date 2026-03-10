import time
from typing import Any

import requests


class RateLimitError(Exception):
    """Represent CRM rate-limit response.
    Args:
        None: No arguments."""


def build_headers(access_token: str) -> dict[str, str]:
    """Build request headers for CRM API.
    Args:
        access_token (str): CRM access token."""
    return {'Authorization': f'Bearer {access_token}'}


def build_params(page_size: int, cursor: str | None) -> dict[str, Any]:
    """Build query params for bulk request.
    Args:
        page_size (int): Number of items per page.
        cursor (str | None): Cursor for next page."""
    params: dict[str, Any] = {'limit': page_size}

    if cursor:
        params['after'] = cursor

    return params


def wait_retry(response: requests.Response) -> int:
    """Read retry delay from rate-limit response.
    Args:
        response (requests.Response): HTTP response object."""
    retry_after = response.headers.get('Retry-After', '10')
    return int(retry_after)


def fetch_page(
    api_url: str,
    access_token: str,
    page_size: int,
    cursor: str | None,
    timeout_sec: int,
) -> dict[str, Any]:
    """Fetch one page from CRM API.
    Args:
        api_url (str): CRM endpoint URL.
        access_token (str): CRM access token.
        page_size (int): Number of items per page.
        cursor (str | None): Cursor for next page.
        timeout_sec (int): Request timeout in seconds."""
    headers = build_headers(access_token=access_token)
    params = build_params(page_size=page_size, cursor=cursor)

    response = requests.get(
        api_url,
        headers=headers,
        params=params,
        timeout=timeout_sec,
    )

    if response.status_code == 429:
        raise RateLimitError(str(wait_retry(response=response)))

    response.raise_for_status()
    return response.json()


def fetch_bulk(
    api_url: str,
    access_token: str,
    page_size: int,
    timeout_sec: int,
) -> list[list[dict[str, Any]]]:
    """Fetch CRM data in batches with cursor pagination.
    Args:
        api_url (str): CRM endpoint URL.
        access_token (str): CRM access token.
        page_size (int): Number of items per page.
        timeout_sec (int): Request timeout in seconds."""
    all_batches: list[list[dict[str, Any]]] = []
    cursor: str | None = None

    while True:
        try:
            page_data = fetch_page(
                api_url=api_url,
                access_token=access_token,
                page_size=page_size,
                cursor=cursor,
                timeout_sec=timeout_sec,
            )
        except RateLimitError as error:
            wait_sec = int(str(error))
            time.sleep(wait_sec)
            continue

        items = page_data.get('items', [])
        if not items:
            break

        all_batches.append(items)

        cursor = (
            page_data.get('paging', {})
            .get('next', {})
            .get('after')
        )
        if not cursor:
            break

    return all_batches


if __name__ == '__main__':
    crm_api_url = 'https://crm.example.com/api/v1/leads'
    crm_access_token = 'YOUR_ACCESS_TOKEN'

    synced_batches = fetch_bulk(
        api_url=crm_api_url,
        access_token=crm_access_token,
        page_size=100,
        timeout_sec=30,
    )

    for batch in synced_batches:
        print(f'Synchronisiert: {len(batch)} Datensätze')
