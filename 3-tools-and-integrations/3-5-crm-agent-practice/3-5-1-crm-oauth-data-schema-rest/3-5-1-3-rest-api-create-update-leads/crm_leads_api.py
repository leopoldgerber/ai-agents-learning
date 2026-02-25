import requests
from typing import Any, Dict, Optional


def build_auth_headers(access_token: str) -> Dict[str, str]:
    """Build auth headers for CRM API.
    Args:
        access_token (str): OAuth access token."""
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }


def create_lead(
    api_base_url: str,
    access_token: str,
    lead_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """Create a lead via CRM REST API.
    Args:
        api_base_url (str): CRM API base URL.
        access_token (str): OAuth access token.
        lead_payload (Dict[str, Any]): Lead payload."""
    url = f'{api_base_url.rstrip("/")}/leads'
    headers = build_auth_headers(access_token=access_token)

    response = requests.post(
        url,
        headers=headers,
        json=lead_payload,
        timeout=10,
    )

    if response.status_code == 201:
        return response.json()

    raise ValueError(
        'Lead creation failed: '
        f'{response.status_code} {response.text}'
    )


def update_lead(
    api_base_url: str,
    access_token: str,
    lead_id: str,
    update_payload: Dict[str, Any],
    method: str = 'patch',
) -> Dict[str, Any]:
    """Update a lead via CRM REST API.
    Args:
        api_base_url (str): CRM API base URL.
        access_token (str): OAuth access token.
        lead_id (str): Lead identifier.
        update_payload (Dict[str, Any]): Fields to update.
        method (str): Update method: 'patch' or 'put'."""
    url = f'{api_base_url.rstrip("/")}/leads/{lead_id}'
    headers = build_auth_headers(access_token=access_token)

    http_method = method.strip().lower()
    if http_method not in {'patch', 'put'}:
        raise ValueError('method must be patch or put')

    request_fn = requests.patch if http_method == 'patch' else requests.put

    response = request_fn(
        url,
        headers=headers,
        json=update_payload,
        timeout=10,
    )

    if response.status_code in {200, 204}:
        if response.status_code == 204:
            return {'ok': True, 'lead_id': lead_id}
        return response.json()

    raise ValueError(
        'Lead update failed: '
        f'{response.status_code} {response.text}'
    )


def safe_error_message(error: Exception) -> str:
    """Build safe error message for user-facing output.
    Args:
        error (Exception): Raised exception."""
    message = str(error)
    if len(message) > 300:
        return message[:300] + '...'
    return message


if __name__ == '__main__':
    api_url = 'https://api.crm.com'
    token = 'your_access_token'

    lead_data = {
        'lead': {
            'name': 'Ivan Ivanov',
            'email': 'ivan@example.com',
            'phone': '+79991234567',
        }
    }

    try:
        created_lead = create_lead(
            api_base_url=api_url,
            access_token=token,
            lead_payload=lead_data,
        )
        print('Created lead:', created_lead)

        lead_id_value: Optional[str] = None
        if isinstance(created_lead, dict):
            lead_id_value = created_lead.get('id')

        if not lead_id_value:
            lead_id_value = '12345'

        updated_lead = update_lead(
            api_base_url=api_url,
            access_token=token,
            lead_id=lead_id_value,
            update_payload={'lead': {'status': 'in_progress'}},
            method='patch',
        )
        print('Updated lead:', updated_lead)
    except ValueError as error:
        print('Error:', safe_error_message(error))
