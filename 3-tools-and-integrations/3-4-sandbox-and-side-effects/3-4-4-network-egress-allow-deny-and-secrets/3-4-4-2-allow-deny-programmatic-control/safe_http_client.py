from typing import Set
from urllib.parse import urlparse

import requests


def normalize_host(url: str) -> str:
    """Extract and normalize hostname from URL.
    Args:
        url (str): Full URL string."""
    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if ':' in host:
        host = host.split(':')[0]

    return host


def validate_host(
    host: str,
    allowed_hosts: Set[str],
    denied_hosts: Set[str],
) -> str:
    """Validate host against allow and deny lists.
    Args:
        host (str): Hostname to validate.
        allowed_hosts (Set[str]): Allowed hostnames.
        denied_hosts (Set[str]): Denied hostnames."""
    if allowed_hosts and host not in allowed_hosts:
        raise ValueError(f'Host {host} not in allow-list')

    if host in denied_hosts:
        raise ValueError(f'Host {host} is denied')

    if host in {'localhost', '127.0.0.1', '0.0.0.0'}:
        raise ValueError(f'Access to {host} is forbidden')

    return host


def safe_get_request(
    url: str,
    allowed_hosts: Set[str],
    denied_hosts: Set[str],
) -> requests.Response:
    """Perform safe GET request with host validation.
    Args:
        url (str): Target URL.
        allowed_hosts (Set[str]): Allowed hostnames.
        denied_hosts (Set[str]): Denied hostnames."""
    host = normalize_host(url=url)

    validate_host(
        host=host,
        allowed_hosts=allowed_hosts,
        denied_hosts=denied_hosts,
    )

    response = requests.get(url, timeout=10)
    return response


if __name__ == '__main__':
    allowed = {'example.com', 'github.com'}
    denied = {'malicious-site.com'}

    try:
        response = safe_get_request(
            url='https://github.com',
            allowed_hosts=allowed,
            denied_hosts=denied,
        )
        print('Status:', response.status_code)
    except ValueError as error:
        print('Blocked:', error)
