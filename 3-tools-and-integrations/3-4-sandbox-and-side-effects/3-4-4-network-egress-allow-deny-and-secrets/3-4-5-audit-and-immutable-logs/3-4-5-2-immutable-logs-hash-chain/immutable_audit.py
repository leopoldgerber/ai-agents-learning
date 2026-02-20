import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def calculate_hash(payload: Dict[str, Any]) -> str:
    """Calculate SHA256 hash for payload.
    Args:
        payload (Dict[str, Any]): Log entry payload."""
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(',', ':'),
    )
    return hashlib.sha256(serialized.encode()).hexdigest()


def build_log_entry(
    index: int,
    prev_hash: str,
    user: str,
    action: str,
    resource: str,
    status: str,
) -> Dict[str, Any]:
    """Build audit entry with hash chain.
    Args:
        index (int): Entry index.
        prev_hash (str): Hash of previous entry.
        user (str): User identifier.
        action (str): Executed action.
        resource (str): Target resource.
        status (str): Operation result."""
    entry = {
        'index': index,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'user': user,
        'action': action,
        'resource': resource,
        'status': status,
        'prev_hash': prev_hash,
    }

    entry_hash = calculate_hash(payload=entry)
    entry['hash'] = entry_hash
    return entry


def verify_chain(
    chain: List[Dict[str, Any]],
) -> Tuple[bool, Optional[int]]:
    """Verify integrity of hash chain.
    Args:
        chain (List[Dict[str, Any]]): List of log entries."""
    for i, entry in enumerate(chain):
        expected_prev = chain[i - 1]['hash'] if i > 0 else '0' * 64

        if entry['prev_hash'] != expected_prev:
            return False, i

        recalculated = calculate_hash(
            payload={
                k: v
                for k, v in entry.items()
                if k != 'hash'
            }
        )

        if entry['hash'] != recalculated:
            return False, i

    return True, None


if __name__ == '__main__':
    audit_chain: List[Dict[str, Any]] = []

    first_entry = build_log_entry(
        index=0,
        prev_hash='0' * 64,
        user='alice',
        action='login',
        resource='auth',
        status='success',
    )
    audit_chain.append(first_entry)

    second_entry = build_log_entry(
        index=1,
        prev_hash=first_entry['hash'],
        user='agent_1',
        action='tool_call',
        resource='external_api',
        status='success',
    )
    audit_chain.append(second_entry)

    is_valid, invalid_index = verify_chain(chain=audit_chain)
    print('Chain valid:', is_valid)

    audit_chain[1]['user'] = 'eve'

    is_valid, invalid_index = verify_chain(chain=audit_chain)
    print('After tampering valid:', is_valid)
    print('Invalid index:', invalid_index)
