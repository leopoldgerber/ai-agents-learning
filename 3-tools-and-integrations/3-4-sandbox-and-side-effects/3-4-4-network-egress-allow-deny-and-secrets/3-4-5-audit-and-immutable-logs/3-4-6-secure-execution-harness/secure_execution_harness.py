import ast
import hashlib
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple


def validate_code_ast(code: str) -> Tuple[bool, List[str]]:
    """Validate code using simple AST checks.
    Args:
        code (str): Python source code."""
    forbidden = {'os', 'sys', 'subprocess', 'eval', 'exec'}
    errors: List[str] = []

    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        return False, [str(error)]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in forbidden:
                    errors.append(
                        f'Forbidden import: {alias.name}'
                    )

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in forbidden:
                    errors.append(
                        f'Forbidden call: {node.func.id}'
                    )

    return len(errors) == 0, errors


def execute_code_sandbox(
    code: str,
    timeout: int,
) -> Dict[str, str]:
    """Execute code in subprocess with timeout.
    Args:
        code (str): Python source code.
        timeout (int): Timeout in seconds."""
    result = subprocess.run(
        ['python', '-c', code],
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    return {
        'stdout': result.stdout,
        'stderr': result.stderr,
        'return_code': str(result.returncode),
    }


def write_audit_entry(
    user: str,
    status: str,
    code: str,
) -> Dict[str, str]:
    """Write structured audit entry.
    Args:
        user (str): User identifier.
        status (str): Execution status.
        code (str): Executed code."""
    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'user': user,
        'status': status,
        'code_hash': hashlib.sha256(
            code.encode()
        ).hexdigest()[:16],
    }

    logging.info(json.dumps(entry))
    return entry


if __name__ == '__main__':
    logging.basicConfig(
        filename='audit.log',
        level=logging.INFO,
        format='%(message)s',
    )

    user_code = "print('Hello secure world')"

    is_valid, errors = validate_code_ast(code=user_code)

    if not is_valid:
        print('Validation failed:', errors)
    else:
        result = execute_code_sandbox(
            code=user_code,
            timeout=3,
        )

        status = 'success'
        if result['return_code'] != '0':
            status = 'failure'

        write_audit_entry(
            user='alice',
            status=status,
            code=user_code,
        )

        print(result['stdout'])
