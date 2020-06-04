from flask_restful import Resource, request
from server.models.postgres.task_manager import TaskManager
from server.services.authentication_service import AuthenticationService
import base64


class AuthenticationApi(Resource):
    def post(self):
        task_manager = TaskManager.get(request.json["id"])
        token = AuthenticationService.generate_session_token(
            task_manager.id
        )
        encoded_token = str(base64.b64encode(token.encode()), "utf-8")
        return {"message": encoded_token}, 201
