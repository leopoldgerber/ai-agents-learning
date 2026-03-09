import hashlib
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


def build_lead_id(email: str) -> str:
    """Build deterministic lead identifier.
    Args:
        email (str): Lead email address."""
    email_value = email.strip().lower()
    lead_hash = hashlib.sha256(email_value.encode('utf-8')).hexdigest()
    return lead_hash[:16]


def build_headers(access_token: str) -> dict[str, str]:
    """Build request headers for CRM API.
    Args:
        access_token (str): CRM access token."""
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }


def create_payload(name: str, email: str) -> dict[str, str]:
    """Build CRM payload for lead creation.
    Args:
        name (str): Lead name.
        email (str): Lead email address."""
    external_id = build_lead_id(email=email)
    return {
        'external_id': external_id,
        'name': name,
        'email': email,
        'status': 'new',
    }


def create_lead(
    api_url: str,
    access_token: str,
    name: str,
    email: str,
    timeout_sec: int,
) -> dict[str, Any]:
    """Create lead without duplicate records.
    Args:
        api_url (str): CRM leads endpoint.
        access_token (str): CRM access token.
        name (str): Lead name.
        email (str): Lead email address.
        timeout_sec (int): Request timeout in seconds."""
    payload = create_payload(name=name, email=email)
    headers = build_headers(access_token=access_token)

    response = requests.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=timeout_sec,
    )

    if response.status_code == 409:
        return {
            'status': 'exists',
            'external_id': payload['external_id'],
            'email': email,
        }

    response.raise_for_status()

    return {
        'status': 'created',
        'external_id': payload['external_id'],
        'email': email,
    }


if __name__ == '__main__':
    crm_api_url = 'https://crm.example.com/api/leads'
    crm_access_token = 'YOUR_ACCESS_TOKEN'
    lead_result = create_lead(
        api_url=crm_api_url,
        access_token=crm_access_token,
        name='Ivan Ivanov',
        email='ivan@example.com',
        timeout_sec=10,
    )
    print(lead_result)
