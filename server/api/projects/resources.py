from flask_restful import Resource, request
import requests
from json2xml import json2xml
from json2xml.utils import readfromstring
import json
import os
import base64
from server.constants import  (
    GITHUB_API_ENDPOINT,
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
        document = json.dumps(request_json)
        data = readfromstring(document)
        document_xml = json2xml.Json2xml(data, wrapper="document", pretty=True).to_xml()
        encoded_xml = base64.b64encode(bytes(document_xml, 'utf-8'))
        project_id = str(request_json["project"]["id"])
        request_data = {
            "message": "Add project " + project_id,
            "committer": {
                "name": GITHUB_COMMITER_NAME,
                "email": GITHUB_COMMITER_EMAIL
            },
            "content": encoded_xml
        }
        request_data["content"] = request_data["content"].decode("utf-8")
        filename = "project" + project_id + ".xml"
        r = requests.put(
            GITHUB_API_ENDPOINT +
            f"repos/{GITHUB_REPOSITORY}/contents/github_files/{filename}",
            headers=headers,
            data=json.dumps(request_data)
        )
        return {"Message": "Success"}, 200
