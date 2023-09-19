# NOTE: Avoid making changes to this file.
# Application-specific logic can be implemented in the `helpers` directory.

from flask import Flask, request, abort, jsonify
from datetime import datetime

from helpers.auth.verify_token import validate_access_token
from helpers.search.main import search_by_email
from helpers.delete.main import delete_by_email

app = Flask(__name__)
app.config.from_prefixed_env()


@app.before_request
def authenticate():
    if request.endpoint == "health_check":
        return

    if request.args.get("email") is None:
        error_response = create_error_response("missing email query parameter")
        return jsonify(error_response), 500

    auth_header = request.headers.get("Authorization")
    if auth_header is None or not validate_access_token(auth_header.split(" ")[-1]):
        abort(403)


@app.route("/health")
def health_check():
    return "Server is up and running"


@app.route("/search", methods=["GET"])
def search():
    try:
        resp = search_by_email(request.args.get("email"))
        return resp, 200
    except Exception as e:
        error_response = create_error_response(e)
        return jsonify(error_response), 500


@app.route("/delete", methods=["DELETE"])
def delete():
    try:
        delete_by_email(request.args.get("email"))
        return [], 204
    except Exception as e:
        error_response = create_error_response(e)
        return jsonify(error_response), 500


def create_error_response(message):
    return {
        "error": {
            "description": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    }
