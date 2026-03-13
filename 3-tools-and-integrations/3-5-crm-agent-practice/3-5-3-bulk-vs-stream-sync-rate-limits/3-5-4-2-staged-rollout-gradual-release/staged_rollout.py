from flask import Flask, request, jsonify


app = Flask(__name__)


ROLLOUT_PERCENTAGE = 10


def is_new_version_enabled(user_id: str) -> bool:
    """Check if user is included in rollout.
    Args:
        user_id (str): Unique user identifier."""
    hash_value = hash(user_id) % 100
    return hash_value < ROLLOUT_PERCENTAGE


def create_lead_v1(data: dict) -> dict:
    """Old lead creation logic.
    Args:
        data (dict): Lead data."""
    return {'status': 'created', 'version': 'v1'}


def create_lead_v2(data: dict) -> dict:
    """New lead creation logic.
    Args:
        data (dict): Lead data."""
    return {'status': 'created', 'version': 'v2'}


@app.route('/create-lead', methods=['POST'])
def create_lead():
    payload = request.json

    user_id = payload.get('user_id')
    lead_data = payload.get('lead_data')

    if is_new_version_enabled(user_id):
        result = create_lead_v2(lead_data)
    else:
        result = create_lead_v1(lead_data)

    return jsonify(result)


if __name__ == '__main__':
    app.run()
