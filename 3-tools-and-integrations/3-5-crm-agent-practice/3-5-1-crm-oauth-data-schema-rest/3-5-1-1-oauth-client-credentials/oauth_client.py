import requests
from typing import Dict


def request_access_token(
    client_id: str,
    client_secret: str,
    token_url: str,
    scope: str,
) -> str:
    """Request OAuth access token using client credentials.
    Args:
        client_id (str): Application client ID.
        client_secret (str): Application client secret.
        token_url (str): OAuth token endpoint.
        scope (str): Requested access scope."""
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope,
    }

    response = requests.post(
        token_url,
        data=payload,
        timeout=10,
    )

    if response.status_code != 200:
        raise ValueError(
            f'Token request failed: '
            f'{response.status_code}'
        )

    token_data: Dict[str, str] = response.json()
    access_token = token_data.get('access_token')

    if not access_token:
        raise ValueError('Access token not found in response')

    return access_token


def build_auth_header(
    access_token: str,
) -> Dict[str, str]:
    """Build Authorization header.
    Args:
        access_token (str): OAuth access token."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    return headers


if __name__ == '__main__':
    token_endpoint = 'https://api.crm.com/oauth/token'

    try:
        token = request_access_token(
            client_id='your_client_id',
            client_secret='your_client_secret',
            token_url=token_endpoint,
            scope='leads.read leads.write',
        )

        headers = build_auth_header(
            access_token=token,
        )

        print('Token received successfully')
        print(headers)

    except ValueError as error:
        print('Error:', error)
