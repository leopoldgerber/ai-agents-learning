import os


def load_secret_value(secret_name: str) -> str:
    """Load secret value from environment.
    Args:
        secret_name (str): Environment variable name."""
    secret_value = os.getenv(secret_name)

    if not secret_value:
        raise ValueError(f'Secret {secret_name} is not set')

    return secret_value


def build_auth_header(api_key: str) -> dict[str, str]:
    """Build authorization header using API key.
    Args:
        api_key (str): Secret API key."""
    headers = {'Authorization': f'Bearer {api_key}'}
    return headers


if __name__ == '__main__':
    os.environ['API_KEY'] = 'demo_key'

    api_key_value = load_secret_value(secret_name='API_KEY')
    auth_headers = build_auth_header(api_key=api_key_value)

    print(auth_headers)
