from flask_restful import Resource, request
from server.models.postgres.task_manager import TaskManager
from server.models.serializers.task_manager import TaskManagerSchema
from server.services.authentication_service import AuthenticationService, token_auth
from server import db
from flask import make_response
import base64


class AuthenticationApi(Resource):
    @token_auth.login_required
    def get(self):
        print(token_auth.current_user())
        return {"message": "success"}


    def post(self):
        task_manager = TaskManager.get(request.json["id"])
        token = AuthenticationService.generate_session_token_for_task_manager(task_manager.id)
        encoded_token = str(base64.b64encode(token.encode()), "utf-8")
        return {"message": encoded_token}, 201
