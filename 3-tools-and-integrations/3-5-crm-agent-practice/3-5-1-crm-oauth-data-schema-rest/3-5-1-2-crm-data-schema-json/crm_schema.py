import json
from typing import Dict


def build_lead_payload(
    name: str,
    email: str,
    phone: str,
) -> Dict[str, Dict[str, str]]:
    """Build JSON payload for CRM lead.
    Args:
        name (str): Lead full name.
        email (str): Lead email.
        phone (str): Lead phone number."""
    payload = {
        'lead': {
            'name': name,
            'email': email,
            'phone': phone,
        }
    }

    return payload


def validate_lead_payload(
    payload: Dict[str, Dict[str, str]],
) -> Dict[str, Dict[str, str]]:
    """Validate required fields in lead payload.
    Args:
        payload (Dict[str, Dict[str, str]]): Lead JSON payload."""
    lead_data = payload.get('lead')

    if not lead_data:
        raise ValueError('Missing lead object')

    required_fields = {'name', 'email', 'phone'}

    for field in required_fields:
        if field not in lead_data:
            raise ValueError(f'Missing required field: {field}')

    return payload


def serialize_payload(
    payload: Dict[str, Dict[str, str]],
) -> str:
    """Serialize payload to JSON string.
    Args:
        payload (Dict[str, Dict[str, str]]): Lead payload."""
    return json.dumps(payload)


if __name__ == '__main__':
    lead_payload = build_lead_payload(
        name='Ivan Ivanov',
        email='ivan@example.com',
        phone='+79991234567',
    )

    validated_payload = validate_lead_payload(
        payload=lead_payload,
    )

    json_string = serialize_payload(
        payload=validated_payload,
    )

    print(json_string)
