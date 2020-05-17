from flask_restful import Resource, request
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


class ProjectApi(Resource):
    def get(self):
        return {"Success": "Hello"}, 200

    def post(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + GITHUB_TOKEN
        }
        request_json = request.get_json()
        document_yaml = yaml.dump(request_json, allow_unicode=True)
        encoded_yaml = base64.b64encode(bytes(document_yaml, 'utf-8'))
        project_id = str(request_json["project"]["id"])
        request_data = {
            "message": "Add project " + project_id,
            "committer": {
                "name": GITHUB_COMMITER_NAME,
                "email": GITHUB_COMMITER_EMAIL
            },
            "content": encoded_yaml
        }
        request_data["content"] = request_data["content"].decode("utf-8")
        filename = "project" + project_id + ".yaml"
        requests.put(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/contents/github_files/{filename}",
            headers=headers,
            data=json.dumps(request_data)
        )
        return {"Message": "Success"}, 200
