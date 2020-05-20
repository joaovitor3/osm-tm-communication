import base64
import binascii

from flask import current_app, request
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_httpauth import HTTPTokenAuth

token_auth = HTTPTokenAuth(scheme="Token")


@token_auth.verify_token
def verify_token(token):
    """ Verify the supplied token """
    if not token:
        return False

    try:
        decoded_token = base64.b64decode(token).decode("utf-8")
    except binascii.Error:
        current_app.logger.debug(f"Unable to decode token {request.base_url}")
        return False  # Can't decode token, so fail login

    valid_token, task_manager_id = AuthenticationService.is_valid_token(
        decoded_token,
        604800
    )
    if not valid_token:
        current_app.logger.debug(f"Token not valid {request.base_url}")
        return False

    return task_manager_id


class AuthenticationService:
    @staticmethod
    def generate_session_token(task_manager_id: int):
        """
        Generates a unique token with the
        task_manager_id and current time embedded within it
        :param task_manager_id: OSM ID of the user authenticating
        :return: Token
        """
        entropy = (
            current_app.secret_key if current_app.secret_key else
            "un1testingmode"
        )

        serializer = URLSafeTimedSerializer(entropy)
        return serializer.dumps(task_manager_id)

    @staticmethod
    def is_valid_token(token, token_expiry):
        """
        Validates if the supplied token is valid, and hasn't expired.
        :param token: Token to check
        :param token_expiry: When the token expires in seconds
        :return: True if token is valid, and user_id contained in token
        """

        entropy = (
            current_app.secret_key if current_app.secret_key else
            "un1testingmode"
        )
        serializer = URLSafeTimedSerializer(entropy)

        try:
            tokenised_task_manager_id = serializer.loads(
                token,
                max_age=token_expiry
            )
        except SignatureExpired:
            current_app.logger.debug("Token has expired")
            return False, None
        except BadSignature:
            current_app.logger.debug("Bad Token Signature")
            return False, None

        return True, tokenised_task_manager_id
