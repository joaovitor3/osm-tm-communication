from flask_restful import Resource, request
from flask import make_response, current_app
from server.models.postgres.document import Document
from server.models.serializers.document import DocumentSchema
from server.services.github_service import GithubService
from server.models.postgres.utils import NotFound
from server.services.authentication_service import token_auth
from requests.exceptions import HTTPError


class DocumentApi(Resource):
    def get(self):
        result = Document.query.all()
        return make_response(DocumentSchema(many=True).jsonify(result), 201)

    @token_auth.login_required
    def post(self):
        try:
            github_obj = GithubService()
            task_manager_id = token_auth.current_user()
            github_file = github_obj.create_or_update_github_file(
                request.json,
                task_manager_id
            )
            return {"Success": f"File created {github_file}"}, 200
        except NotFound as e:
            current_app.logger.error(
                f"Error validating task manager: {str(e)}"
            )
            return {"Error": "Task Manager not found"}, 404
        except HTTPError as e:
            current_app.logger.error(f"Error validating document: {str(e)}")
            return {"Error": f"{str(e)}"}, 409

    @token_auth.login_required
    def put(self, project_id):
        try:
            github_obj = GithubService()
            github_file = github_obj.create_or_update_github_file(
                request.json,
                project_id,
                True
            )
            return {"Success": f"File updated {github_file}"}, 200
        except NotFound as e:
            current_app.logger.error(
                f"Error validating task manager: {str(e)}"
            )
            return {"Error": "Task Manager not found"}, 404
