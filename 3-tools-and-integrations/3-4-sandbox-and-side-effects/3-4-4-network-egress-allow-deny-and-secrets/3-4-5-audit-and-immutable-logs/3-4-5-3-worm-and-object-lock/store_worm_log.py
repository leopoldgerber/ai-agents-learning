import json
from datetime import datetime, timedelta
from typing import Any, Dict

import boto3


def build_log_payload(
    user: str,
    action: str,
    resource: str,
) -> Dict[str, Any]:
    """Build log payload for storage.
    Args:
        user (str): User identifier.
        action (str): Executed action.
        resource (str): Target resource."""
    payload = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'user': user,
        'action': action,
        'resource': resource,
    }
    return payload


def store_worm_entry(
    payload: Dict[str, Any],
    bucket_name: str,
) -> Dict[str, Any]:
    """Store audit entry with Object Lock enabled.
    Args:
        payload (Dict[str, Any]): Log payload.
        bucket_name (str): S3 bucket name."""
    s3_client = boto3.client('s3')

    timestamp_key = datetime.utcnow().strftime(
        '%Y%m%d_%H%M%S_%f'
    )
    object_key = f'audit-logs/{timestamp_key}.json'

    retention_date = datetime.utcnow() + timedelta(days=365)

    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=json.dumps(payload),
        ObjectLockMode='COMPLIANCE',
        ObjectLockRetainUntilDate=retention_date,
    )

    return payload


if __name__ == '__main__':
    log_payload = build_log_payload(
        user='agent_1',
        action='delete_resource',
        resource='document_123',
    )

    print('Payload prepared for WORM storage:')
    print(log_payload)
