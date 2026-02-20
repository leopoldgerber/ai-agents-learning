import json
import logging
from datetime import datetime
from typing import Any, Dict


def configure_logger(log_file: str) -> None:
    """Configure structured JSON logger.
    Args:
        log_file (str): Path to log file."""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(message)s',
    )


def build_audit_entry(
    user: str,
    action: str,
    resource: str,
    status: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:
    """Build structured audit log entry.
    Args:
        user (str): User identifier.
        action (str): Executed action.
        resource (str): Target resource.
        status (str): Operation result.
        details (Dict[str, Any]): Additional context."""
    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'user': user,
        'action': action,
        'resource': resource,
        'status': status,
        'details': details,
        'ip_address': '192.168.1.10',
        'session_id': 'session_123',
    }
    return entry


def write_audit_log(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Write audit entry to log file.
    Args:
        entry (Dict[str, Any]): Structured audit entry."""
    logging.info(json.dumps(entry))
    return entry


if __name__ == '__main__':
    configure_logger(log_file='audit.log')

    login_entry = build_audit_entry(
        user='alice',
        action='login',
        resource='auth_system',
        status='success',
        details={'method': 'password'},
    )
    write_audit_log(entry=login_entry)

    tool_entry = build_audit_entry(
        user='agent_1',
        action='tool_call',
        resource='external_api',
        status='success',
        details={'endpoint': '/v1/data', 'response_ms': 240},
    )
    write_audit_log(entry=tool_entry)

    print('Audit entries written to audit.log')
