from typing import Any, Dict
from agent_repository import AgentRepository


def validate_agent_payload(agent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate minimal agent payload.
    Args:
        agent_data (dict[str, Any]): Incoming agent payload."""
    name_value = str(agent_data.get('name', '')).strip()
    email_value = str(agent_data.get('email', '')).strip()

    errors_list: list[str] = []
    if not name_value:
        errors_list.append('name is required')
    if not email_value or '@' not in email_value:
        errors_list.append('email is invalid')

    if errors_list:
        return {'ok': False, 'errors': errors_list}

    return {'ok': True, 'data': {'name': name_value, 'email': email_value}}


def create_agent_with_limit(
    repo: AgentRepository,
    agent_data: Dict[str, Any],
    max_agents_per_email: int,
) -> Dict[str, Any]:
    """Create agent with a simple business rule limit.
    Args:
        repo (AgentRepository): Data repository.
        agent_data (dict[str, Any]): Agent payload.
        max_agents_per_email (int): Max agents allowed per email."""
    validation = validate_agent_payload(agent_data=agent_data)
    if not validation.get('ok'):
        return {
            'ok': False,
            'error': 'validation_failed',
            'details': validation.get('errors', [])
        }

    normalized = validation['data']
    email_value = normalized['email']

    with repo.connection.cursor() as cur:
        cur.execute(
            'SELECT COUNT(*) FROM agents WHERE email = %s', (email_value,))
        count_value = int(cur.fetchone()[0])

    if count_value >= max_agents_per_email:
        return {
            'ok': False,
            'error': 'limit_exceeded',
            'email': email_value,
            'limit': max_agents_per_email
        }

    repo.create_agent(agent_data=normalized)

    return {'ok': True, 'result': 'created', 'email': email_value}


def get_agent_or_error(repo: AgentRepository, agent_id: int) -> Dict[str, Any]:
    """Get agent by id and return a service-level response.
    Args:
        repo (AgentRepository): Data repository.
        agent_id (int): Agent identifier."""
    agent = repo.get_agent(agent_id=agent_id)
    if agent is None:
        return {'ok': False, 'error': 'not_found', 'agent_id': agent_id}

    return {'ok': True, 'agent': agent}


def update_agent_profile(
    repo: AgentRepository,
    agent_id: int,
    agent_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Update agent profile and return service-level response.
    Args:
        repo (AgentRepository): Data repository.
        agent_id (int): Agent identifier.
        agent_data (dict[str, Any]): Updated agent payload."""
    validation = validate_agent_payload(agent_data=agent_data)
    if not validation.get('ok'):
        return {
            'ok': False,
            'error': 'validation_failed',
            'details': validation.get('errors', [])
        }

    existing = repo.get_agent(agent_id=agent_id)
    if existing is None:
        return {
            'ok': False,
            'error': 'not_found',
            'agent_id': agent_id
        }

    repo.update_agent(agent_id=agent_id, agent_data=validation['data'])
    return {'ok': True, 'result': 'updated', 'agent_id': agent_id}


def delete_agent_profile(
        repo: AgentRepository,
        agent_id: int
) -> Dict[str, Any]:
    """Delete agent profile and return service-level response.
    Args:
        repo (AgentRepository): Data repository.
        agent_id (int): Agent identifier."""
    existing = repo.get_agent(agent_id=agent_id)
    if existing is None:
        return {'ok': False, 'error': 'not_found', 'agent_id': agent_id}

    repo.delete_agent(agent_id=agent_id)
    return {'ok': True, 'result': 'deleted', 'agent_id': agent_id}
