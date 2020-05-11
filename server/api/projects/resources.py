from flask_restful import Resource, request
import requests
from json2xml import json2xml
from json2xml.utils import readfromstring
import json
import os
import base64

GITHUB_API_ENDPOINT = "https://api.github.com/"

class ProjectApi(Resource):
    def get(self):
        return {"Success": "Hello"}, 200

    def post(self):
        token = os.getenv("GITHUB_TOKEN")
        github_repository = os.getenv("GITHUB_REPOSITORY")
        github_commiter_name = os.getenv("GITHUB_COMMITER_NAME")
        github_commiter_email = os.getenv("GITHUB_COMMITER_EMAIL")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        }
        request_json = request.get_json()
        document = json.dumps(request_json)
        data = readfromstring(document)
        document_xml = json2xml.Json2xml(data, wrapper="document", pretty=True).to_xml()
        encoded_xml = base64.b64encode(bytes(document_xml, 'utf-8'))
        project_id = str(request_json["project"]["id"])
        request_data = {
            "message": "Add project " + project_id,
            "committer": {
                "name": github_commiter_name,
                "email": github_commiter_email
            },
            "content": encoded_xml
        }
        request_data["content"] = request_data["content"].decode("utf-8")
        filename = "project" + project_id + ".xml"
        r = requests.put(
            GITHUB_API_ENDPOINT +
            f"repos/{github_repository}/contents/github_files/{filename}",
            headers=headers,
            data=json.dumps(request_data)
        )
        return {"Message": "Success"}, 200
