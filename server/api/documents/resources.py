from flask_restful import Resource, request
from flask import current_app
from server.services.github_service import (
    GithubService,
    GithubServiceError
)
from server.models.serializers.document import (
    DocumentSchema,
    is_known_document_content_type,
    turn_fields_optional
)
from marshmallow.exceptions import ValidationError


class DocumentApi(Resource):
    def post(self):
        try:
            github_obj = GithubService()
            github_document_schema = DocumentSchema()
            github_document_data = (
                github_document_schema.load(request.json)
            )
            github_file = github_obj.create_or_update_github_file(
                github_document_data,
                update_file=False
            )
            return {"Success": f"File created {github_file}"}, 200
        except GithubServiceError as e:
            current_app.logger.error(f"Error validating document: {str(e)}")
            return {"Error": f"{str(e)}"}, 409

    def put(self, project_id):
        try:
            content_type = request.args.getlist('contentType')
            is_known_document_content_type(content_type)

            optional_fields = turn_fields_optional(content_type)
            github_document_schema = DocumentSchema(
                partial=optional_fields,
                only=optional_fields
            )
            github_document_data = (
                github_document_schema.load(request.json)
            )

            github_obj = GithubService()
            github_file = github_obj.create_or_update_github_file(
                github_document_data,
                update_file=True,
                github_project_id=project_id
            )
            return {"Success": f"File updated {github_file}"}, 200
        except ValidationError as e:
            return {"Error": f"{str(e)}"}, 404
