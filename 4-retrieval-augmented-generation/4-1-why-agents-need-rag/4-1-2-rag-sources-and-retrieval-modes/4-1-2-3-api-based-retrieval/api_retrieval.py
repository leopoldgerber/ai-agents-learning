from typing import Any
import requests


def fetch_data(api_url: str, timeout_sec: int) -> list[dict[str, Any]]:
    """Fetch data from external API.
    Args:
        api_url (str): API endpoint.
        timeout_sec (int): Request timeout."""
    response = requests.get(api_url, timeout=timeout_sec)

    if response.status_code == 200:
        return response.json()

    return []


def extract_titles(data: list[dict[str, Any]]) -> list[str]:
    """Extract titles from API response.
    Args:
        data (list): API response data."""
    return [item.get('title', '') for item in data]


if __name__ == "__main__":
    api_url = "https://api.example.com/research/ai"

    articles = fetch_data(api_url, timeout_sec=10)

    titles = extract_titles(articles)

    for title in titles:
        print(title)
