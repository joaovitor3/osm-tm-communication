from flask_restful import Resource, request
from flask import make_response
import requests
import yaml
import json
import base64
from server.constants import (
    GITHUB_TOKEN,
    GITHUB_REPOSITORY,
    GITHUB_COMMITER_NAME,
    GITHUB_COMMITER_EMAIL,
    GITHUB_API_ENDPOINT,
)
from server.models.postgres.document import Document
from server.models.postgres.task_manager import TaskManager
from server.models.serializers.document import DocumentSchema
from server import db
from server.services.github_service import GithubService


class DocumentApi(Resource):
    def get(self):
        result = Document.query.all()
        return make_response(DocumentSchema(many=True).jsonify(result), 201)

    def post(self):
        github_obj = GithubService()
        tasking_manager_id = request.json["taskManager"]
        response_content = github_obj.create_file(request.json)
        
        document_link = response_content["content"]["html_url"]
        document_commit_hash = response_content["commit"]["sha"]
        document = Document()
        document.create_document(document_link, document_commit_hash, tasking_manager_id)
        document.save()

        return {"Message": "Success"}, 200
