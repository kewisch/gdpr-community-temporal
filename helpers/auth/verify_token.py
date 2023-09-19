import logging
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime
import os


def validate_access_token(token):
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=os.getenv("GDPR_AUDIENCE"),
        )

        expiration_timestamp = id_info.get("exp")
        current_timestamp = datetime.utcnow().timestamp()

        if expiration_timestamp is None or current_timestamp > expiration_timestamp:
            raise Exception("Expired token")

        email = id_info.get("email")

        return (
            id_info.get("email_verified")
            and email is not None
            and email == os.getenv("GDPR_SA_EMAIL")
        )
    except Exception as e:
        logging.error(f"Token validation error: {e}")
        return False
