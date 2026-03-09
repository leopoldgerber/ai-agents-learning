import requests
from typing import Any


def build_headers(access_token: str) -> dict[str, str]:
    """Build request headers for CRM API.
    Args:
        access_token (str): CRM access token."""
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }


def build_update_payload(
    status: str | None,
    phone: str | None,
    email: str | None,
) -> dict[str, str]:
    """Build payload with fields to update.
    Args:
        status (str | None): Lead status value.
        phone (str | None): Lead phone number.
        email (str | None): Lead email address."""
    payload: dict[str, str] = {}

    if status:
        payload['status'] = status

    if phone:
        payload['phone'] = phone

    if email:
        payload['email'] = email

    return payload


def update_lead(
    api_url: str,
    access_token: str,
    lead_id: str,
    status: str | None,
    phone: str | None,
    email: str | None,
    timeout_sec: int,
) -> dict[str, Any]:
    """Update existing lead in CRM.
    Args:
        api_url (str): CRM leads endpoint.
        access_token (str): CRM access token.
        lead_id (str): Lead identifier.
        status (str | None): New lead status.
        phone (str | None): Updated phone number.
        email (str | None): Updated email address.
        timeout_sec (int): Request timeout in seconds."""
    payload = build_update_payload(
        status=status,
        phone=phone,
        email=email,
    )

    headers = build_headers(access_token=access_token)

    response = requests.patch(
        f'{api_url}/{lead_id}',
        headers=headers,
        json=payload,
        timeout=timeout_sec,
    )

    response.raise_for_status()

    return response.json()


if __name__ == '__main__':
    crm_api_url = 'https://crm.example.com/api/leads'
    crm_access_token = 'YOUR_ACCESS_TOKEN'

    lead_result = update_lead(
        api_url=crm_api_url,
        access_token=crm_access_token,
        lead_id='lead_12345',
        status='contacted',
        phone='+7 999 123-45-67',
        email=None,
        timeout_sec=10,
    )

    print(lead_result)
