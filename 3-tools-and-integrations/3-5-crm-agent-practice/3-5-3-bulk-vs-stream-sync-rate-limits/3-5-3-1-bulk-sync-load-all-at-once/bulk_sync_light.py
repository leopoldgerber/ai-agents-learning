import requests
from tenacity import (
    retry, stop_after_attempt, wait_exponential, retry_if_exception_type)

# CRM settings
API_URL = "http://127.0.0.1:8000/api/v1/leads"
TOKEN = "your_access_token"


class RateLimitError(Exception):
    """Custom exception for rate limit exceeded"""
    pass


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(
        (requests.exceptions.RequestException, RateLimitError)
    )
)
def make_request(url, params):
    """Request wrapper with automatic retries
    for network errors and rate limits"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, params=params, headers=headers, timeout=30)

    if response.status_code == 429:
        # If the API returned Retry-After, raise a custom exception
        wait_time = int(response.headers.get("Retry-After", 10))
        raise RateLimitError(
            f"Rate limit hit, retry after {wait_time} seconds")

    response.raise_for_status()
    return response.json()


def fetch_bulk(page_size=100):
    """Load data using cursor-based pagination"""
    cursor = None  # No cursor at the start

    while True:
        params = {"limit": page_size}
        if cursor:
            # In other CRMs this may be "offset" or "paging"
            params["after"] = cursor

        data = make_request(API_URL, params)
        items = data.get("items", [])

        if not items:
            break

        # Save the current batch before yield to avoid losing data
        yield items

        # Get the pointer to the next page (HubSpot/Pipedrive style)
        cursor = data.get("paging", {}).get("next", {}).get("after")
        if not cursor:
            break


if __name__ == '__main__':
    try:
        for batch in fetch_bulk():
            # process_batch(batch)
            print(f"Synchronized: {len(batch)} records")
            # You can store the last successful cursor
            # in the database for recovery
    except Exception as e:
        print(f"Critical synchronization error: {e}")
