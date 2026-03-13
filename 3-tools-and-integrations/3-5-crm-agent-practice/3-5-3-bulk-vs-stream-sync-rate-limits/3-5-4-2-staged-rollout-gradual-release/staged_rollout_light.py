from flask import Flask, request, jsonify

app = Flask(__name__)

# Percentage of users who receive the new version
ROLLOUT_PERCENTAGE = 10


# Feature flag: whether the new logic is enabled
def is_new_version_enabled(user_id: str) -> bool:
    """Deterministically determine
    whether the user is included in the rollout"""
    # Use a hash of user_id for stable distribution
    hash_value = hash(user_id) % 100
    return hash_value < ROLLOUT_PERCENTAGE


@app.route('/create-lead', methods=['POST'])
def create_lead():
    user_id = request.json.get('user_id')
    lead_data = request.json.get('lead_data')

    if is_new_version_enabled(user_id):
        # New lead creation logic
        result = create_lead_v2(lead_data)
        return jsonify({"version": "v2", "result": result})
    else:
        # Old, stable logic
        result = create_lead_v1(lead_data)
        return jsonify({"version": "v1", "result": result})


def create_lead_v1(data):
    return {"status": "created", "method": "old"}


def create_lead_v2(data):
    return {"status": "created", "method": "new"}


if __name__ == '__main__':
    app.run()
